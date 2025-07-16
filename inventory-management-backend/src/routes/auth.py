from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from datetime import datetime, timedelta
from src.models.inventory import db, User, Organization
import json

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """User authentication and JWT token generation"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        if not user.organization.is_active:
            return jsonify({'error': 'Organization is deactivated'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create JWT tokens
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=timedelta(days=30)
        )
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(include_sensitive=True),
            'organization': user.organization.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@auth_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """JWT token refresh for extended sessions"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        new_token = create_access_token(
            identity=current_user_id,
            expires_delta=timedelta(hours=24)
        )
        
        return jsonify({
            'access_token': new_token,
            'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Token refresh failed', 'details': str(e)}), 500

@auth_bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Token invalidation and session termination"""
    # In a production environment, you would add the token to a blacklist
    # For now, we'll just return a success message
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """Register new organization and admin user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['organization_name', 'organization_email', 'username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if organization slug already exists
        org_slug = data['organization_name'].lower().replace(' ', '-').replace('_', '-')
        existing_org = Organization.query.filter_by(slug=org_slug).first()
        if existing_org:
            return jsonify({'error': 'Organization name already exists'}), 409
        
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        if existing_user:
            return jsonify({'error': 'Username or email already exists'}), 409
        
        # Create organization
        organization = Organization(
            name=data['organization_name'],
            slug=org_slug,
            email=data['organization_email'],
            phone=data.get('organization_phone'),
            address=data.get('organization_address'),
            settings=json.dumps({
                'timezone': 'UTC',
                'currency': 'USD',
                'date_format': 'YYYY-MM-DD'
            })
        )
        db.session.add(organization)
        db.session.flush()  # Get the organization ID
        
        # Create admin user
        user = User(
            organization_id=organization.id,
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role='admin',
            permissions=json.dumps({
                'manage_users': True,
                'manage_inventory': True,
                'manage_reports': True,
                'manage_settings': True
            })
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Organization and admin user created successfully',
            'organization': organization.to_dict(),
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict(include_sensitive=True),
            'organization': user.organization.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user info', 'details': str(e)}), 500

