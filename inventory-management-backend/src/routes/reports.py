from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func, desc, text
from src.models.inventory import (
    db, User, Product, Category, Warehouse, Inventory, 
    InventoryMovement, Supplier, PurchaseOrder
)

reports_bp = Blueprint('reports', __name__)

def get_current_user():
    """Helper function to get current user"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)

@reports_bp.route('/reports/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics and overview"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        org_id = user.organization_id
        
        # Total products
        total_products = db.session.query(func.count(Product.id)).filter_by(
            organization_id=org_id, is_active=True
        ).scalar()
        
        # Total warehouses
        total_warehouses = db.session.query(func.count(Warehouse.id)).filter_by(
            organization_id=org_id, is_active=True
        ).scalar()
        
        # Low stock items
        low_stock_items = db.session.query(func.count(Inventory.id)).join(Product).filter(
            and_(
                Inventory.organization_id == org_id,
                Inventory.quantity_on_hand <= Product.minimum_stock_level,
                Product.is_active == True
            )
        ).scalar()
        
        # Total inventory value (using cost price)
        inventory_value_result = db.session.query(
            func.sum(Inventory.quantity_on_hand * Product.cost_price)
        ).join(Product).filter(
            and_(
                Inventory.organization_id == org_id,
                Product.cost_price.isnot(None),
                Product.is_active == True
            )
        ).scalar()
        
        total_inventory_value = float(inventory_value_result) if inventory_value_result else 0
        
        # Recent movements (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_movements = db.session.query(func.count(InventoryMovement.id)).filter(
            and_(
                InventoryMovement.organization_id == org_id,
                InventoryMovement.movement_date >= seven_days_ago
            )
        ).scalar()
        
        # Top 5 products by quantity
        top_products = db.session.query(
            Product.name,
            Product.sku,
            func.sum(Inventory.quantity_on_hand).label('total_quantity')
        ).join(Inventory).filter(
            and_(
                Product.organization_id == org_id,
                Product.is_active == True
            )
        ).group_by(Product.id, Product.name, Product.sku).order_by(
            desc('total_quantity')
        ).limit(5).all()
        
        # Recent movements for activity feed
        recent_activity = db.session.query(InventoryMovement).filter_by(
            organization_id=org_id
        ).order_by(desc(InventoryMovement.movement_date)).limit(10).all()
        
        # Movement trends (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        movement_trends = db.session.query(
            func.date(InventoryMovement.movement_date).label('date'),
            InventoryMovement.movement_type,
            func.count(InventoryMovement.id).label('count')
        ).filter(
            and_(
                InventoryMovement.organization_id == org_id,
                InventoryMovement.movement_date >= thirty_days_ago
            )
        ).group_by(
            func.date(InventoryMovement.movement_date),
            InventoryMovement.movement_type
        ).order_by('date').all()
        
        return jsonify({
            'summary': {
                'total_products': total_products,
                'total_warehouses': total_warehouses,
                'low_stock_items': low_stock_items,
                'total_inventory_value': total_inventory_value,
                'recent_movements': recent_movements
            },
            'top_products': [
                {
                    'name': product.name,
                    'sku': product.sku,
                    'total_quantity': int(product.total_quantity)
                }
                for product in top_products
            ],
            'recent_activity': [movement.to_dict() for movement in recent_activity],
            'movement_trends': [
                {
                    'date': trend.date.isoformat() if trend.date else None,
                    'movement_type': trend.movement_type,
                    'count': trend.count
                }
                for trend in movement_trends
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get dashboard stats', 'details': str(e)}), 500

@reports_bp.route('/reports/inventory-summary', methods=['GET'])
@jwt_required()
def get_inventory_summary():
    """Generate comprehensive inventory summary report"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        org_id = user.organization_id
        warehouse_id = request.args.get('warehouse_id', type=int)
        category_id = request.args.get('category_id', type=int)
        
        # Base query for inventory summary
        query = db.session.query(
            Product.name.label('product_name'),
            Product.sku,
            Category.name.label('category_name'),
            Warehouse.name.label('warehouse_name'),
            Inventory.quantity_on_hand,
            Inventory.quantity_reserved,
            (Inventory.quantity_on_hand - Inventory.quantity_reserved).label('quantity_available'),
            Product.cost_price,
            Product.selling_price,
            (Inventory.quantity_on_hand * Product.cost_price).label('total_cost_value'),
            (Inventory.quantity_on_hand * Product.selling_price).label('total_selling_value')
        ).select_from(Inventory).join(Product).join(Warehouse).outerjoin(Category).filter(
            Inventory.organization_id == org_id
        )
        
        # Apply filters
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        inventory_data = query.all()
        
        # Calculate totals
        total_cost_value = sum(
            float(item.total_cost_value) if item.total_cost_value else 0 
            for item in inventory_data
        )
        total_selling_value = sum(
            float(item.total_selling_value) if item.total_selling_value else 0 
            for item in inventory_data
        )
        total_items = len(inventory_data)
        total_quantity = sum(item.quantity_on_hand for item in inventory_data)
        
        # Group by category
        by_category = {}
        for item in inventory_data:
            category = item.category_name or 'Uncategorized'
            if category not in by_category:
                by_category[category] = {
                    'items': 0,
                    'total_quantity': 0,
                    'total_cost_value': 0,
                    'total_selling_value': 0
                }
            
            by_category[category]['items'] += 1
            by_category[category]['total_quantity'] += item.quantity_on_hand
            by_category[category]['total_cost_value'] += float(item.total_cost_value) if item.total_cost_value else 0
            by_category[category]['total_selling_value'] += float(item.total_selling_value) if item.total_selling_value else 0
        
        # Group by warehouse
        by_warehouse = {}
        for item in inventory_data:
            warehouse = item.warehouse_name
            if warehouse not in by_warehouse:
                by_warehouse[warehouse] = {
                    'items': 0,
                    'total_quantity': 0,
                    'total_cost_value': 0,
                    'total_selling_value': 0
                }
            
            by_warehouse[warehouse]['items'] += 1
            by_warehouse[warehouse]['total_quantity'] += item.quantity_on_hand
            by_warehouse[warehouse]['total_cost_value'] += float(item.total_cost_value) if item.total_cost_value else 0
            by_warehouse[warehouse]['total_selling_value'] += float(item.total_selling_value) if item.total_selling_value else 0
        
        return jsonify({
            'summary': {
                'total_items': total_items,
                'total_quantity': total_quantity,
                'total_cost_value': total_cost_value,
                'total_selling_value': total_selling_value,
                'potential_profit': total_selling_value - total_cost_value
            },
            'by_category': [
                {
                    'category': category,
                    **stats
                }
                for category, stats in by_category.items()
            ],
            'by_warehouse': [
                {
                    'warehouse': warehouse,
                    **stats
                }
                for warehouse, stats in by_warehouse.items()
            ],
            'detailed_items': [
                {
                    'product_name': item.product_name,
                    'sku': item.sku,
                    'category': item.category_name or 'Uncategorized',
                    'warehouse': item.warehouse_name,
                    'quantity_on_hand': item.quantity_on_hand,
                    'quantity_reserved': item.quantity_reserved,
                    'quantity_available': item.quantity_available,
                    'cost_price': float(item.cost_price) if item.cost_price else None,
                    'selling_price': float(item.selling_price) if item.selling_price else None,
                    'total_cost_value': float(item.total_cost_value) if item.total_cost_value else 0,
                    'total_selling_value': float(item.total_selling_value) if item.total_selling_value else 0
                }
                for item in inventory_data
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to generate inventory summary', 'details': str(e)}), 500

@reports_bp.route('/reports/low-stock', methods=['GET'])
@jwt_required()
def get_low_stock_report():
    """Generate low stock alert report"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        org_id = user.organization_id
        warehouse_id = request.args.get('warehouse_id', type=int)
        threshold_percentage = request.args.get('threshold_percentage', 100, type=int)
        
        # Query for low stock items
        query = db.session.query(
            Product.name.label('product_name'),
            Product.sku,
            Product.minimum_stock_level,
            Product.reorder_point,
            Product.reorder_quantity,
            Warehouse.name.label('warehouse_name'),
            Inventory.quantity_on_hand,
            Inventory.quantity_reserved,
            (Inventory.quantity_on_hand - Inventory.quantity_reserved).label('quantity_available'),
            Category.name.label('category_name')
        ).select_from(Inventory).join(Product).join(Warehouse).outerjoin(Category).filter(
            and_(
                Inventory.organization_id == org_id,
                Product.is_active == True,
                Inventory.quantity_on_hand <= (Product.minimum_stock_level * threshold_percentage / 100)
            )
        )
        
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        
        low_stock_items = query.order_by(
            (Inventory.quantity_on_hand / Product.minimum_stock_level).asc()
        ).all()
        
        # Calculate criticality levels
        critical_items = []
        warning_items = []
        
        for item in low_stock_items:
            if item.minimum_stock_level > 0:
                stock_ratio = item.quantity_on_hand / item.minimum_stock_level
                if stock_ratio <= 0.25:  # 25% or less of minimum stock
                    critical_items.append(item)
                else:
                    warning_items.append(item)
            else:
                warning_items.append(item)
        
        return jsonify({
            'summary': {
                'total_low_stock_items': len(low_stock_items),
                'critical_items': len(critical_items),
                'warning_items': len(warning_items)
            },
            'low_stock_items': [
                {
                    'product_name': item.product_name,
                    'sku': item.sku,
                    'category': item.category_name or 'Uncategorized',
                    'warehouse': item.warehouse_name,
                    'quantity_on_hand': item.quantity_on_hand,
                    'quantity_available': item.quantity_available,
                    'minimum_stock_level': item.minimum_stock_level,
                    'reorder_point': item.reorder_point,
                    'reorder_quantity': item.reorder_quantity,
                    'stock_ratio': (item.quantity_on_hand / item.minimum_stock_level) if item.minimum_stock_level > 0 else 0,
                    'criticality': 'critical' if item in critical_items else 'warning'
                }
                for item in low_stock_items
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to generate low stock report', 'details': str(e)}), 500

@reports_bp.route('/reports/movement-analysis', methods=['GET'])
@jwt_required()
def get_movement_analysis():
    """Generate inventory movement analysis report"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        org_id = user.organization_id
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        product_id = request.args.get('product_id', type=int)
        movement_type = request.args.get('movement_type')
        
        # Default to last 30 days if no dates provided
        if not date_from:
            date_from = (datetime.utcnow() - timedelta(days=30)).isoformat()
        if not date_to:
            date_to = datetime.utcnow().isoformat()
        
        try:
            date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Base query for movements
        query = db.session.query(InventoryMovement).filter(
            and_(
                InventoryMovement.organization_id == org_id,
                InventoryMovement.movement_date >= date_from_obj,
                InventoryMovement.movement_date <= date_to_obj
            )
        )
        
        if product_id:
            query = query.filter(InventoryMovement.product_id == product_id)
        
        if movement_type:
            query = query.filter(InventoryMovement.movement_type == movement_type)
        
        movements = query.all()
        
        # Analyze movements by type
        movement_summary = {}
        for movement in movements:
            mov_type = movement.movement_type
            if mov_type not in movement_summary:
                movement_summary[mov_type] = {
                    'count': 0,
                    'total_quantity': 0,
                    'total_value': 0
                }
            
            movement_summary[mov_type]['count'] += 1
            movement_summary[mov_type]['total_quantity'] += abs(movement.quantity)
            if movement.unit_cost:
                movement_summary[mov_type]['total_value'] += abs(movement.quantity) * float(movement.unit_cost)
        
        # Top products by movement activity
        product_activity = db.session.query(
            Product.name,
            Product.sku,
            func.count(InventoryMovement.id).label('movement_count'),
            func.sum(func.abs(InventoryMovement.quantity)).label('total_quantity_moved')
        ).join(InventoryMovement).filter(
            and_(
                InventoryMovement.organization_id == org_id,
                InventoryMovement.movement_date >= date_from_obj,
                InventoryMovement.movement_date <= date_to_obj
            )
        ).group_by(Product.id, Product.name, Product.sku).order_by(
            desc('movement_count')
        ).limit(10).all()
        
        # Daily movement trends
        daily_trends = db.session.query(
            func.date(InventoryMovement.movement_date).label('date'),
            InventoryMovement.movement_type,
            func.count(InventoryMovement.id).label('count'),
            func.sum(func.abs(InventoryMovement.quantity)).label('total_quantity')
        ).filter(
            and_(
                InventoryMovement.organization_id == org_id,
                InventoryMovement.movement_date >= date_from_obj,
                InventoryMovement.movement_date <= date_to_obj
            )
        ).group_by(
            func.date(InventoryMovement.movement_date),
            InventoryMovement.movement_type
        ).order_by('date').all()
        
        return jsonify({
            'analysis': {
                'date_range': {
                    'from': date_from,
                    'to': date_to
                },
                'total_movements': len(movements),
                'movement_summary': movement_summary
            },
            'top_products': [
                {
                    'name': product.name,
                    'sku': product.sku,
                    'movement_count': product.movement_count,
                    'total_quantity_moved': int(product.total_quantity_moved)
                }
                for product in product_activity
            ],
            'daily_trends': [
                {
                    'date': trend.date.isoformat() if trend.date else None,
                    'movement_type': trend.movement_type,
                    'count': trend.count,
                    'total_quantity': int(trend.total_quantity)
                }
                for trend in daily_trends
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to generate movement analysis', 'details': str(e)}), 500

@reports_bp.route('/reports/valuation', methods=['GET'])
@jwt_required()
def get_inventory_valuation():
    """Generate inventory valuation report"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        org_id = user.organization_id
        warehouse_id = request.args.get('warehouse_id', type=int)
        
        # Query for inventory valuation
        query = db.session.query(
            Product.name.label('product_name'),
            Product.sku,
            Product.cost_price,
            Product.selling_price,
            Warehouse.name.label('warehouse_name'),
            Category.name.label('category_name'),
            Inventory.quantity_on_hand,
            (Inventory.quantity_on_hand * Product.cost_price).label('cost_value'),
            (Inventory.quantity_on_hand * Product.selling_price).label('selling_value'),
            ((Inventory.quantity_on_hand * Product.selling_price) - (Inventory.quantity_on_hand * Product.cost_price)).label('potential_profit')
        ).select_from(Inventory).join(Product).join(Warehouse).outerjoin(Category).filter(
            and_(
                Inventory.organization_id == org_id,
                Inventory.quantity_on_hand > 0,
                Product.is_active == True
            )
        )
        
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        
        valuation_data = query.all()
        
        # Calculate totals
        total_cost_value = sum(
            float(item.cost_value) if item.cost_value else 0 
            for item in valuation_data
        )
        total_selling_value = sum(
            float(item.selling_value) if item.selling_value else 0 
            for item in valuation_data
        )
        total_potential_profit = total_selling_value - total_cost_value
        
        # Top valued items
        top_valued_items = sorted(
            valuation_data,
            key=lambda x: float(x.cost_value) if x.cost_value else 0,
            reverse=True
        )[:10]
        
        return jsonify({
            'summary': {
                'total_cost_value': total_cost_value,
                'total_selling_value': total_selling_value,
                'total_potential_profit': total_potential_profit,
                'profit_margin_percentage': (total_potential_profit / total_cost_value * 100) if total_cost_value > 0 else 0,
                'total_items_valued': len(valuation_data)
            },
            'top_valued_items': [
                {
                    'product_name': item.product_name,
                    'sku': item.sku,
                    'category': item.category_name or 'Uncategorized',
                    'warehouse': item.warehouse_name,
                    'quantity_on_hand': item.quantity_on_hand,
                    'cost_price': float(item.cost_price) if item.cost_price else 0,
                    'selling_price': float(item.selling_price) if item.selling_price else 0,
                    'cost_value': float(item.cost_value) if item.cost_value else 0,
                    'selling_value': float(item.selling_value) if item.selling_value else 0,
                    'potential_profit': float(item.potential_profit) if item.potential_profit else 0
                }
                for item in top_valued_items
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to generate valuation report', 'details': str(e)}), 500

