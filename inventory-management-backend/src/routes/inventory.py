from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from sqlalchemy import and_, or_, func, desc
from src.models.inventory import (
    db, User, Product, Category, Warehouse, Inventory, 
    InventoryMovement, Supplier, PurchaseOrder, PurchaseOrderItem, Alert
)
import json

inventory_bp = Blueprint('inventory', __name__)

def get_current_user():
    """Helper function to get current user"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)

def check_organization_access(user, organization_id):
    """Helper function to check if user has access to organization data"""
    return user.organization_id == organization_id

# Product Management Routes
@inventory_bp.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    """Retrieve product catalog with filtering and search"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        search = request.args.get('search', '')
        category_id = request.args.get('category_id', type=int)
        is_active = request.args.get('is_active', type=bool)
        low_stock = request.args.get('low_stock', type=bool)
        
        # Base query
        query = Product.query.filter_by(organization_id=user.organization_id)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    Product.name.contains(search),
                    Product.sku.contains(search),
                    Product.description.contains(search)
                )
            )
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        if low_stock:
            # Join with inventory to check stock levels
            query = query.join(Inventory).filter(
                Inventory.quantity_on_hand <= Product.minimum_stock_level
            )
        
        # Pagination
        total = query.count()
        products = query.offset((page - 1) * limit).limit(limit).all()
        
        return jsonify({
            'products': [product.to_dict() for product in products],
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve products', 'details': str(e)}), 500

@inventory_bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    """Create new product entry"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['sku', 'name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if SKU already exists in organization
        existing_product = Product.query.filter_by(
            organization_id=user.organization_id,
            sku=data['sku']
        ).first()
        if existing_product:
            return jsonify({'error': 'SKU already exists'}), 409
        
        # Create product
        product = Product(
            organization_id=user.organization_id,
            sku=data['sku'],
            name=data['name'],
            description=data.get('description'),
            category_id=data.get('category_id'),
            brand=data.get('brand'),
            unit_of_measure=data.get('unit_of_measure', 'piece'),
            cost_price=data.get('cost_price'),
            selling_price=data.get('selling_price'),
            minimum_stock_level=data.get('minimum_stock_level', 0),
            maximum_stock_level=data.get('maximum_stock_level'),
            reorder_point=data.get('reorder_point', 0),
            reorder_quantity=data.get('reorder_quantity', 0),
            barcode=data.get('barcode'),
            image_url=data.get('image_url'),
            weight=data.get('weight'),
            dimensions=data.get('dimensions')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'product': product.to_dict(),
            'message': 'Product created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create product', 'details': str(e)}), 500

@inventory_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update product information"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        product = Product.query.filter_by(
            id=product_id,
            organization_id=user.organization_id
        ).first()
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        updatable_fields = [
            'name', 'description', 'category_id', 'brand', 'unit_of_measure',
            'cost_price', 'selling_price', 'minimum_stock_level', 'maximum_stock_level',
            'reorder_point', 'reorder_quantity', 'barcode', 'image_url', 'weight',
            'dimensions', 'is_active'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(product, field, data[field])
        
        product.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'product': product.to_dict(),
            'message': 'Product updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update product', 'details': str(e)}), 500

# Inventory Management Routes
@inventory_bp.route('/inventory', methods=['GET'])
@jwt_required()
def get_inventory():
    """Retrieve current inventory levels across warehouses"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        warehouse_id = request.args.get('warehouse_id', type=int)
        product_id = request.args.get('product_id', type=int)
        low_stock = request.args.get('low_stock', type=bool)
        
        # Base query
        query = Inventory.query.filter_by(organization_id=user.organization_id)
        
        # Apply filters
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        
        if product_id:
            query = query.filter_by(product_id=product_id)
        
        if low_stock:
            query = query.join(Product).filter(
                Inventory.quantity_on_hand <= Product.minimum_stock_level
            )
        
        # Pagination
        total = query.count()
        inventory_items = query.offset((page - 1) * limit).limit(limit).all()
        
        # Calculate summary statistics
        total_products = db.session.query(func.count(Inventory.id)).filter_by(
            organization_id=user.organization_id
        ).scalar()
        
        low_stock_count = db.session.query(func.count(Inventory.id)).join(Product).filter(
            and_(
                Inventory.organization_id == user.organization_id,
                Inventory.quantity_on_hand <= Product.minimum_stock_level
            )
        ).scalar()
        
        return jsonify({
            'inventory': [item.to_dict() for item in inventory_items],
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit,
            'summary': {
                'total_products': total_products,
                'low_stock_count': low_stock_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve inventory', 'details': str(e)}), 500

@inventory_bp.route('/inventory/movements', methods=['POST'])
@jwt_required()
def create_inventory_movement():
    """Record inventory movement (receipt, shipment, adjustment)"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['product_id', 'warehouse_id', 'movement_type', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate movement type
        valid_types = ['in', 'out', 'adjustment', 'transfer']
        if data['movement_type'] not in valid_types:
            return jsonify({'error': 'Invalid movement type'}), 400
        
        # Check if product and warehouse belong to user's organization
        product = Product.query.filter_by(
            id=data['product_id'],
            organization_id=user.organization_id
        ).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        warehouse = Warehouse.query.filter_by(
            id=data['warehouse_id'],
            organization_id=user.organization_id
        ).first()
        if not warehouse:
            return jsonify({'error': 'Warehouse not found'}), 404
        
        # Get or create inventory record
        inventory = Inventory.query.filter_by(
            organization_id=user.organization_id,
            product_id=data['product_id'],
            warehouse_id=data['warehouse_id']
        ).first()
        
        if not inventory:
            inventory = Inventory(
                organization_id=user.organization_id,
                product_id=data['product_id'],
                warehouse_id=data['warehouse_id'],
                quantity_on_hand=0
            )
            db.session.add(inventory)
        
        # Validate stock for outbound movements
        quantity = data['quantity']
        if data['movement_type'] in ['out', 'transfer'] and inventory.quantity_on_hand < quantity:
            return jsonify({'error': 'Insufficient stock'}), 409
        
        # Update inventory quantity
        if data['movement_type'] == 'in':
            inventory.quantity_on_hand += quantity
        elif data['movement_type'] == 'out':
            inventory.quantity_on_hand -= quantity
        elif data['movement_type'] == 'adjustment':
            inventory.quantity_on_hand = quantity  # Set to absolute value for adjustments
        
        inventory.last_movement_at = datetime.utcnow()
        inventory.updated_at = datetime.utcnow()
        
        # Create movement record
        movement = InventoryMovement(
            organization_id=user.organization_id,
            product_id=data['product_id'],
            warehouse_id=data['warehouse_id'],
            movement_type=data['movement_type'],
            quantity=quantity,
            unit_cost=data.get('unit_cost'),
            reference_type=data.get('reference_type'),
            reference_id=data.get('reference_id'),
            notes=data.get('notes'),
            user_id=user.id
        )
        
        db.session.add(movement)
        db.session.commit()
        
        # Check for low stock alerts
        if inventory.quantity_on_hand <= product.minimum_stock_level:
            alert = Alert(
                organization_id=user.organization_id,
                alert_type='low_stock',
                title=f'Low Stock Alert: {product.name}',
                message=f'Product {product.name} (SKU: {product.sku}) is running low in {warehouse.name}. Current stock: {inventory.quantity_on_hand}, Minimum level: {product.minimum_stock_level}',
                severity='warning',
                entity_type='product',
                entity_id=product.id
            )
            db.session.add(alert)
            db.session.commit()
        
        return jsonify({
            'movement': movement.to_dict(),
            'updated_inventory': inventory.to_dict(),
            'message': 'Inventory movement recorded successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to record movement', 'details': str(e)}), 500

@inventory_bp.route('/inventory/movements', methods=['GET'])
@jwt_required()
def get_inventory_movements():
    """Retrieve inventory movement history"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        product_id = request.args.get('product_id', type=int)
        warehouse_id = request.args.get('warehouse_id', type=int)
        movement_type = request.args.get('movement_type')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Base query
        query = InventoryMovement.query.filter_by(organization_id=user.organization_id)
        
        # Apply filters
        if product_id:
            query = query.filter_by(product_id=product_id)
        
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        
        if movement_type:
            query = query.filter_by(movement_type=movement_type)
        
        if date_from:
            try:
                date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(InventoryMovement.movement_date >= date_from_obj)
            except ValueError:
                return jsonify({'error': 'Invalid date_from format'}), 400
        
        if date_to:
            try:
                date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(InventoryMovement.movement_date <= date_to_obj)
            except ValueError:
                return jsonify({'error': 'Invalid date_to format'}), 400
        
        # Order by most recent first
        query = query.order_by(desc(InventoryMovement.movement_date))
        
        # Pagination
        total = query.count()
        movements = query.offset((page - 1) * limit).limit(limit).all()
        
        return jsonify({
            'movements': [movement.to_dict() for movement in movements],
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve movements', 'details': str(e)}), 500

# Warehouse Management Routes
@inventory_bp.route('/warehouses', methods=['GET'])
@jwt_required()
def get_warehouses():
    """Retrieve warehouses for the organization"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        warehouses = Warehouse.query.filter_by(
            organization_id=user.organization_id,
            is_active=True
        ).all()
        
        return jsonify({
            'warehouses': [warehouse.to_dict() for warehouse in warehouses]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve warehouses', 'details': str(e)}), 500

@inventory_bp.route('/warehouses', methods=['POST'])
@jwt_required()
def create_warehouse():
    """Create new warehouse"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'code']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if warehouse code already exists in organization
        existing_warehouse = Warehouse.query.filter_by(
            organization_id=user.organization_id,
            code=data['code']
        ).first()
        if existing_warehouse:
            return jsonify({'error': 'Warehouse code already exists'}), 409
        
        # Create warehouse
        warehouse = Warehouse(
            organization_id=user.organization_id,
            name=data['name'],
            code=data['code'],
            address=data.get('address'),
            manager_id=data.get('manager_id'),
            capacity_limit=data.get('capacity_limit')
        )
        
        db.session.add(warehouse)
        db.session.commit()
        
        return jsonify({
            'warehouse': warehouse.to_dict(),
            'message': 'Warehouse created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create warehouse', 'details': str(e)}), 500

# Category Management Routes
@inventory_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Retrieve categories for the organization"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        categories = Category.query.filter_by(
            organization_id=user.organization_id,
            is_active=True
        ).order_by(Category.sort_order, Category.name).all()
        
        return jsonify({
            'categories': [category.to_dict() for category in categories]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve categories', 'details': str(e)}), 500

@inventory_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    """Create new category"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        # Create category
        category = Category(
            organization_id=user.organization_id,
            name=data['name'],
            description=data.get('description'),
            parent_id=data.get('parent_id'),
            sort_order=data.get('sort_order', 0)
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'category': category.to_dict(),
            'message': 'Category created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create category', 'details': str(e)}), 500

# Alert Management Routes
@inventory_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    """Retrieve alerts for the organization"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        unread_only = request.args.get('unread_only', type=bool)
        
        # Base query
        query = Alert.query.filter_by(organization_id=user.organization_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        # Order by most recent first
        query = query.order_by(desc(Alert.created_at))
        
        # Pagination
        total = query.count()
        alerts = query.offset((page - 1) * limit).limit(limit).all()
        
        return jsonify({
            'alerts': [alert.to_dict() for alert in alerts],
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve alerts', 'details': str(e)}), 500

@inventory_bp.route('/alerts/<int:alert_id>/read', methods=['PUT'])
@jwt_required()
def mark_alert_read(alert_id):
    """Mark alert as read"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        alert = Alert.query.filter_by(
            id=alert_id,
            organization_id=user.organization_id
        ).first()
        
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        alert.is_read = True
        db.session.commit()
        
        return jsonify({
            'alert': alert.to_dict(),
            'message': 'Alert marked as read'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to mark alert as read', 'details': str(e)}), 500

