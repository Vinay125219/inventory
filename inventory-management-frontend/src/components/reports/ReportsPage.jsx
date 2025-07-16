import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart3,
  Download,
  Calendar,
  TrendingUp,
  Package,
  AlertTriangle,
  DollarSign,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { apiClient, formatCurrency, formatDate } from '../../lib/api';
import LoadingSpinner from '../ui/LoadingSpinner';

const ReportsPage = () => {
  const [loading, setLoading] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState('30');
  const [selectedReport, setSelectedReport] = useState('inventory-summary');

  // Sample data for demonstration
  const inventoryTrendData = [
    { month: 'Jan', value: 45000, quantity: 1200 },
    { month: 'Feb', value: 52000, quantity: 1350 },
    { month: 'Mar', value: 48000, quantity: 1180 },
    { month: 'Apr', value: 61000, quantity: 1420 },
    { month: 'May', value: 55000, quantity: 1300 },
    { month: 'Jun', value: 67000, quantity: 1580 },
  ];

  const topProductsData = [
    { name: 'Laptop Pro 15"', value: 25000, quantity: 50, color: '#3B82F6' },
    { name: 'Wireless Headphones', value: 18000, quantity: 120, color: '#10B981' },
    { name: 'Smartphone X', value: 22000, quantity: 40, color: '#F59E0B' },
    { name: 'Tablet Air', value: 15000, quantity: 75, color: '#EF4444' },
    { name: 'Smart Watch', value: 12000, quantity: 80, color: '#8B5CF6' },
  ];

  const movementAnalysisData = [
    { date: '2024-01-01', inbound: 150, outbound: 120 },
    { date: '2024-01-02', inbound: 180, outbound: 140 },
    { date: '2024-01-03', inbound: 120, outbound: 160 },
    { date: '2024-01-04', inbound: 200, outbound: 180 },
    { date: '2024-01-05', inbound: 160, outbound: 140 },
    { date: '2024-01-06', inbound: 140, outbound: 100 },
    { date: '2024-01-07', inbound: 100, outbound: 80 },
  ];

  const lowStockItems = [
    { id: 1, name: 'Wireless Mouse', sku: 'WM001', current_stock: 5, min_level: 20, status: 'critical' },
    { id: 2, name: 'USB Cable', sku: 'UC001', current_stock: 15, min_level: 50, status: 'low' },
    { id: 3, name: 'Power Adapter', sku: 'PA001', current_stock: 8, min_level: 25, status: 'critical' },
    { id: 4, name: 'Keyboard', sku: 'KB001', current_stock: 12, min_level: 30, status: 'low' },
  ];

  const ReportCard = ({ title, value, icon: Icon, trend, trendValue, color = 'blue' }) => {
    const colorClasses = {
      blue: 'from-blue-500 to-blue-600',
      green: 'from-green-500 to-green-600',
      orange: 'from-orange-500 to-orange-600',
      purple: 'from-purple-500 to-purple-600',
    };

    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">{title}</p>
              <p className="text-2xl font-bold">{value}</p>
              {trend && (
                <div className="flex items-center mt-2">
                  <TrendingUp className={`w-4 h-4 mr-1 ${trend === 'up' ? 'text-green-500' : 'text-red-500'}`} />
                  <span className={`text-sm ${trend === 'up' ? 'text-green-500' : 'text-red-500'}`}>
                    {trendValue}
                  </span>
                </div>
              )}
            </div>
            <div className={`p-3 rounded-full bg-gradient-to-r ${colorClasses[color]}`}>
              <Icon className="w-6 h-6 text-white" />
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reports & Analytics</h1>
          <p className="text-muted-foreground">
            Comprehensive insights into your inventory performance.
          </p>
        </div>
        <div className="flex space-x-2">
          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
              <SelectItem value="365">Last year</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <ReportCard
            title="Total Inventory Value"
            value={formatCurrency(567000)}
            icon={DollarSign}
            trend="up"
            trendValue="+12.5%"
            color="green"
          />
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <ReportCard
            title="Total Products"
            value="1,247"
            icon={Package}
            trend="up"
            trendValue="+8.2%"
            color="blue"
          />
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <ReportCard
            title="Low Stock Items"
            value="23"
            icon={AlertTriangle}
            trend="down"
            trendValue="-15.3%"
            color="orange"
          />
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <ReportCard
            title="Turnover Rate"
            value="4.2x"
            icon={TrendingUp}
            trend="up"
            trendValue="+5.7%"
            color="purple"
          />
        </motion.div>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Inventory Value Trend */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Inventory Value Trend</CardTitle>
              <CardDescription>Monthly inventory value and quantity trends</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={inventoryTrendData}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value, name) => [
                    name === 'value' ? formatCurrency(value) : value,
                    name === 'value' ? 'Value' : 'Quantity'
                  ]} />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#3B82F6"
                    fillOpacity={1}
                    fill="url(#colorValue)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Top Products by Value */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Top Products by Value</CardTitle>
              <CardDescription>Highest value products in inventory</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={topProductsData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {topProductsData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [formatCurrency(value), 'Value']} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Movement Analysis */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Movement Analysis</CardTitle>
            <CardDescription>Daily inbound vs outbound movements</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={movementAnalysisData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tickFormatter={(value) => new Date(value).toLocaleDateString()} />
                <YAxis />
                <Tooltip labelFormatter={(value) => new Date(value).toLocaleDateString()} />
                <Legend />
                <Bar dataKey="inbound" fill="#10B981" name="Inbound" />
                <Bar dataKey="outbound" fill="#EF4444" name="Outbound" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </motion.div>

      {/* Low Stock Alert */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.7 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Low Stock Alert</CardTitle>
            <CardDescription>Items that need immediate attention</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Product</TableHead>
                    <TableHead>SKU</TableHead>
                    <TableHead>Current Stock</TableHead>
                    <TableHead>Minimum Level</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Action Needed</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {lowStockItems.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell className="font-medium">{item.name}</TableCell>
                      <TableCell className="font-mono text-sm">{item.sku}</TableCell>
                      <TableCell>{item.current_stock}</TableCell>
                      <TableCell>{item.min_level}</TableCell>
                      <TableCell>
                        <Badge variant={item.status === 'critical' ? 'destructive' : 'secondary'}>
                          {item.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Button size="sm" variant="outline">
                          Reorder {item.min_level - item.current_stock + 10} units
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default ReportsPage;

