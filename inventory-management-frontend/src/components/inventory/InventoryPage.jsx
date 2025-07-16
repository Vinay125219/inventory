import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  Download,
  Upload,
  Package,
  TrendingUp,
  TrendingDown,
  MoreHorizontal,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { apiClient, formatCurrency, formatDate, getStockStatus } from '../../lib/api';
import LoadingSpinner from '../ui/LoadingSpinner';

const InventoryPage = () => {
  const [inventory, setInventory] = useState([]);
  const [products, setProducts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedWarehouse, setSelectedWarehouse] = useState('');
  const [showMovementDialog, setShowMovementDialog] = useState(false);
  const [movementData, setMovementData] = useState({
    product_id: '',
    warehouse_id: '',
    movement_type: 'in',
    quantity: '',
    unit_cost: '',
    reference: '',
    notes: '',
  });

  useEffect(() => {
    fetchInventory();
    fetchProducts();
    fetchWarehouses();
  }, []);

  const fetchInventory = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getInventory({
        search: searchTerm,
        warehouse_id: selectedWarehouse,
      });
      setInventory(data.inventory || []);
    } catch (error) {
      console.error('Error fetching inventory:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchProducts = async () => {
    try {
      const data = await apiClient.getProducts();
      setProducts(data.products || []);
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

  const fetchWarehouses = async () => {
    try {
      const data = await apiClient.getWarehouses();
      setWarehouses(data.warehouses || []);
    } catch (error) {
      console.error('Error fetching warehouses:', error);
    }
  };

  const handleMovement = async (e) => {
    e.preventDefault();
    try {
      const movement = {
        ...movementData,
        quantity: parseInt(movementData.quantity),
        unit_cost: movementData.unit_cost ? parseFloat(movementData.unit_cost) : null,
      };

      await apiClient.createInventoryMovement(movement);
      setShowMovementDialog(false);
      setMovementData({
        product_id: '',
        warehouse_id: '',
        movement_type: 'in',
        quantity: '',
        unit_cost: '',
        reference: '',
        notes: '',
      });
      fetchInventory();
    } catch (error) {
      console.error('Error creating movement:', error);
    }
  };

  const getStockStatusBadge = (item) => {
    const status = getStockStatus(item.quantity, item.product?.minimum_stock_level || 0);
    
    const variants = {
      'out-of-stock': 'destructive',
      'low-stock': 'secondary',
      'medium-stock': 'outline',
      'in-stock': 'default',
    };

    return (
      <Badge variant={variants[status.status]}>
        {status.status.replace('-', ' ')}
      </Badge>
    );
  };

  const filteredInventory = inventory.filter(item => {
    const matchesSearch = item.product?.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.product?.sku.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesWarehouse = !selectedWarehouse || item.warehouse_id?.toString() === selectedWarehouse;
    return matchesSearch && matchesWarehouse;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Inventory</h1>
          <p className="text-muted-foreground">
            Track stock levels and manage inventory movements.
          </p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          <Dialog open={showMovementDialog} onOpenChange={setShowMovementDialog}>
            <DialogTrigger asChild>
              <Button className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700">
                <Plus className="w-4 h-4 mr-2" />
                Record Movement
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Record Inventory Movement</DialogTitle>
                <DialogDescription>
                  Add or remove stock from your inventory
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleMovement} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="product">Product *</Label>
                    <Select
                      value={movementData.product_id}
                      onValueChange={(value) => setMovementData({ ...movementData, product_id: value })}
                      required
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select product" />
                      </SelectTrigger>
                      <SelectContent>
                        {products.map((product) => (
                          <SelectItem key={product.id} value={product.id.toString()}>
                            {product.name} ({product.sku})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="warehouse">Warehouse *</Label>
                    <Select
                      value={movementData.warehouse_id}
                      onValueChange={(value) => setMovementData({ ...movementData, warehouse_id: value })}
                      required
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select warehouse" />
                      </SelectTrigger>
                      <SelectContent>
                        {warehouses.map((warehouse) => (
                          <SelectItem key={warehouse.id} value={warehouse.id.toString()}>
                            {warehouse.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="movement_type">Movement Type *</Label>
                    <Select
                      value={movementData.movement_type}
                      onValueChange={(value) => setMovementData({ ...movementData, movement_type: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="in">Stock In</SelectItem>
                        <SelectItem value="out">Stock Out</SelectItem>
                        <SelectItem value="adjustment">Adjustment</SelectItem>
                        <SelectItem value="transfer">Transfer</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="quantity">Quantity *</Label>
                    <Input
                      id="quantity"
                      type="number"
                      value={movementData.quantity}
                      onChange={(e) => setMovementData({ ...movementData, quantity: e.target.value })}
                      placeholder="0"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="unit_cost">Unit Cost</Label>
                    <Input
                      id="unit_cost"
                      type="number"
                      step="0.01"
                      value={movementData.unit_cost}
                      onChange={(e) => setMovementData({ ...movementData, unit_cost: e.target.value })}
                      placeholder="0.00"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="reference">Reference</Label>
                  <Input
                    id="reference"
                    value={movementData.reference}
                    onChange={(e) => setMovementData({ ...movementData, reference: e.target.value })}
                    placeholder="PO#, Invoice#, etc."
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="notes">Notes</Label>
                  <Input
                    id="notes"
                    value={movementData.notes}
                    onChange={(e) => setMovementData({ ...movementData, notes: e.target.value })}
                    placeholder="Additional notes"
                  />
                </div>

                <div className="flex justify-end space-x-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowMovementDialog(false)}
                  >
                    Cancel
                  </Button>
                  <Button type="submit">Record Movement</Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Search inventory by product name or SKU..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={selectedWarehouse} onValueChange={setSelectedWarehouse}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="All Warehouses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Warehouses</SelectItem>
                {warehouses.map((warehouse) => (
                  <SelectItem key={warehouse.id} value={warehouse.id.toString()}>
                    {warehouse.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button onClick={fetchInventory}>
              <Search className="w-4 h-4 mr-2" />
              Search
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Inventory Table */}
      <Card>
        <CardHeader>
          <CardTitle>Current Stock ({filteredInventory.length})</CardTitle>
          <CardDescription>
            Real-time inventory levels across all warehouses.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <LoadingSpinner />
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Product</TableHead>
                    <TableHead>SKU</TableHead>
                    <TableHead>Warehouse</TableHead>
                    <TableHead>Current Stock</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Value</TableHead>
                    <TableHead>Last Updated</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredInventory.length > 0 ? (
                    filteredInventory.map((item) => (
                      <motion.tr
                        key={`${item.product_id}-${item.warehouse_id}`}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="hover:bg-gray-50"
                      >
                        <TableCell>
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-blue-500 rounded-lg flex items-center justify-center">
                              <Package className="w-5 h-5 text-white" />
                            </div>
                            <div>
                              <div className="font-medium">{item.product?.name}</div>
                              <div className="text-sm text-muted-foreground">
                                {item.product?.brand || 'No brand'}
                              </div>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="font-mono text-sm">{item.product?.sku}</TableCell>
                        <TableCell>{item.warehouse?.name}</TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            <span className="font-medium">{item.quantity}</span>
                            <span className="text-sm text-muted-foreground">
                              {item.product?.unit_of_measure}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>{getStockStatusBadge(item)}</TableCell>
                        <TableCell>
                          {item.product?.cost_price
                            ? formatCurrency(item.quantity * item.product.cost_price)
                            : '-'}
                        </TableCell>
                        <TableCell>{formatDate(item.last_updated)}</TableCell>
                      </motion.tr>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8">
                        <div className="flex flex-col items-center space-y-2">
                          <Package className="w-8 h-8 text-muted-foreground" />
                          <p className="text-muted-foreground">No inventory found</p>
                          <Button
                            variant="outline"
                            onClick={() => setShowMovementDialog(true)}
                          >
                            Record your first movement
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default InventoryPage;

