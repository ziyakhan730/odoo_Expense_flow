import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { 
  CheckCircle, XCircle, Clock, Search, Filter, Eye, 
  Calendar, User, DollarSign, FileText, ChevronLeft, ChevronRight,
  Download, RefreshCw, FileSpreadsheet
} from 'lucide-react';
import { apiService } from '../services/api';
import { toast } from 'sonner';

interface Expense {
  id: number;
  title: string;
  description: string;
  amount: number;
  currency: string;
  status: string;
  priority: string;
  expense_date: string;
  submission_date: string;
  user_name: string;
  category?: {
    name: string;
  };
  approved_by_name?: string;
  approved_at?: string;
  rejection_reason?: string;
}

interface HistoryData {
  expenses: Expense[];
  pagination: {
    page: number;
    page_size: number;
    total_count: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
  };
  summary: {
    total: number;
    approved: number;
    rejected: number;
    pending: number;
  };
}

const ManagerHistory: React.FC = () => {
  const [historyData, setHistoryData] = useState<HistoryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedExpense, setSelectedExpense] = useState<Expense | null>(null);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  
  // Filter states
  const [filters, setFilters] = useState({
    status: 'all',
    employee: '',
    date_from: '',
    date_to: '',
    search: '',
    page: 1,
    page_size: 20
  });

  useEffect(() => {
    loadHistoryData();
  }, [filters]);

  const loadHistoryData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Prepare filters for API call - convert "all" to empty string
      const apiFilters = {
        ...filters,
        status: filters.status === 'all' ? '' : filters.status
      };
      
      const data = await apiService.getManagerApprovalHistory(apiFilters);
      setHistoryData(data);
    } catch (err: any) {
      console.error('Error loading history data:', err);
      setError(err.message || 'Failed to load approval history');
      // Set empty data structure to prevent crashes
      setHistoryData({
        expenses: [],
        pagination: {
          page: 1,
          page_size: 20,
          total_count: 0,
          total_pages: 0,
          has_next: false,
          has_previous: false
        },
        summary: {
          total: 0,
          approved: 0,
          rejected: 0,
          pending: 0
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      page: 1 // Reset to first page when filters change
    }));
  };

  const clearFilters = () => {
    setFilters({
      status: 'all',
      employee: '',
      date_from: '',
      date_to: '',
      search: '',
      page: 1,
      page_size: 20
    });
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: { variant: 'secondary' as const, icon: Clock, text: 'Pending', color: 'text-yellow-600' },
      approved: { variant: 'default' as const, icon: CheckCircle, text: 'Approved', color: 'text-green-600' },
      rejected: { variant: 'destructive' as const, icon: XCircle, text: 'Rejected', color: 'text-red-600' },
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;
    const Icon = config.icon;
    
    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className={`h-3 w-3 ${config.color}`} />
        {config.text}
      </Badge>
    );
  };

  const getPriorityBadge = (priority: string) => {
    const priorityConfig = {
      low: { variant: 'secondary' as const, text: 'Low' },
      medium: { variant: 'default' as const, text: 'Medium' },
      high: { variant: 'destructive' as const, text: 'High' },
      urgent: { variant: 'destructive' as const, text: 'Urgent' },
    };
    
    const config = priorityConfig[priority as keyof typeof priorityConfig] || priorityConfig.medium;
    
    return (
      <Badge variant={config.variant}>
        {config.text}
      </Badge>
    );
  };

  const handlePageChange = (newPage: number) => {
    setFilters(prev => ({ ...prev, page: newPage }));
  };

  const exportToExcel = async (exportType: 'all' | 'approved' | 'pending' | 'rejected') => {
    try {
      setExportLoading(true);
      
      // Prepare filters for export
      const exportFilters = {
        ...filters,
        status: exportType === 'all' ? '' : exportType,
        page: 1,
        page_size: 1000 // Get all records for export
      };
      
      // Fetch data for export
      const data = await apiService.getManagerApprovalHistory(exportFilters);
      
      // Generate Excel file
      const excelData = generateExcelData(data.expenses, exportType);
      downloadExcelFile(excelData, exportType);
      
      // Show success message
      toast.success(`Exported ${data.expenses.length} ${exportType} expenses successfully!`);
      
      setExportDialogOpen(false);
    } catch (err: any) {
      console.error('Export error:', err);
      toast.error('Failed to export data. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const generateExcelData = (expenses: Expense[], exportType: string) => {
    const headers = [
      'ID',
      'Title',
      'Description',
      'Amount',
      'Currency',
      'Status',
      'Priority',
      'Employee',
      'Expense Date',
      'Submission Date',
      'Category',
      'Approved By',
      'Approved At',
      'Rejection Reason'
    ];

    const rows = expenses.map(expense => [
      expense.id,
      expense.title,
      expense.description || '',
      expense.amount,
      expense.currency,
      expense.status,
      expense.priority,
      expense.user_name,
      new Date(expense.expense_date).toLocaleDateString(),
      new Date(expense.submission_date).toLocaleDateString(),
      expense.category?.name || '',
      expense.approved_by_name || '',
      expense.approved_at ? new Date(expense.approved_at).toLocaleDateString() : '',
      expense.rejection_reason || ''
    ]);

    return [headers, ...rows];
  };

  const downloadExcelFile = (data: any[][], exportType: string) => {
    // Create CSV content (Excel can open CSV files)
    const csvContent = data.map(row => 
      row.map(cell => `"${cell}"`).join(',')
    ).join('\n');

    // Add BOM for UTF-8 support
    const BOM = '\uFEFF';
    const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' });
    
    // Create download link
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `expense_history_${exportType}_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading approval history...</p>
          <p className="text-sm text-gray-500 mt-1">Fetching data from backend...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Approval History</h1>
          <p className="text-gray-600">Review all expense approvals and decisions</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={loadHistoryData} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button 
            onClick={() => setExportDialogOpen(true)} 
            variant="outline" 
            size="sm"
            disabled={exportLoading}
          >
            <FileSpreadsheet className="h-4 w-4 mr-2" />
            {exportLoading ? 'Exporting...' : 'Export'}
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Summary Cards */}
      {historyData?.summary && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Expenses</CardTitle>
              <FileText className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{historyData.summary.total}</div>
              <p className="text-xs text-muted-foreground">All submitted expenses</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Approved</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{historyData.summary.approved}</div>
              <p className="text-xs text-muted-foreground">Approved expenses</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Rejected</CardTitle>
              <XCircle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{historyData.summary.rejected}</div>
              <p className="text-xs text-muted-foreground">Rejected expenses</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending</CardTitle>
              <Clock className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{historyData.summary.pending}</div>
              <p className="text-xs text-muted-foreground">Awaiting review</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            <div>
              <label className="text-sm font-medium">Status</label>
              <Select value={filters.status} onValueChange={(value) => handleFilterChange('status', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="All Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <label className="text-sm font-medium">Employee</label>
              <Input
                placeholder="Search by employee name"
                value={filters.employee}
                onChange={(e) => handleFilterChange('employee', e.target.value)}
              />
            </div>
            
            <div>
              <label className="text-sm font-medium">From Date</label>
              <Input
                type="date"
                value={filters.date_from}
                onChange={(e) => handleFilterChange('date_from', e.target.value)}
              />
            </div>
            
            <div>
              <label className="text-sm font-medium">To Date</label>
              <Input
                type="date"
                value={filters.date_to}
                onChange={(e) => handleFilterChange('date_to', e.target.value)}
              />
            </div>
            
            <div>
              <label className="text-sm font-medium">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search expenses..."
                  className="pl-10"
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                />
              </div>
            </div>
          </div>
          
          <div className="flex gap-2 mt-4">
            <Button onClick={clearFilters} variant="outline" size="sm">
              Clear Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* History Table */}
      <Card>
        <CardHeader>
          <CardTitle>Expense History</CardTitle>
          <p className="text-sm text-muted-foreground">
            Showing {historyData?.expenses.length || 0} of {historyData?.pagination.total_count || 0} expenses
          </p>
        </CardHeader>
        <CardContent>
          {historyData?.expenses.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No expenses found</h3>
              <p className="text-gray-600 mb-4">No expenses match your current filters.</p>
              <Button onClick={loadHistoryData} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh Data
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {historyData?.expenses.map((expense) => (
                <div
                  key={expense.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-accent/50 transition-colors"
                >
                  <div className="space-y-1 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="font-medium">{expense.title}</p>
                      {getStatusBadge(expense.status)}
                      {getPriorityBadge(expense.priority)}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <User className="h-4 w-4" />
                        <span>{expense.user_name}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        <span>{new Date(expense.expense_date).toLocaleDateString()}</span>
                      </div>
                      {expense.category && (
                        <div className="flex items-center gap-1">
                          <FileText className="h-4 w-4" />
                          <span>{expense.category.name}</span>
                        </div>
                      )}
                    </div>
                    {expense.description && (
                      <p className="text-sm text-gray-600 mt-1">{expense.description}</p>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="font-bold text-lg">
                        {expense.amount} {expense.currency}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Submitted {new Date(expense.submission_date).toLocaleDateString()}
                      </p>
                    </div>
                    
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="outline" size="sm" onClick={() => setSelectedExpense(expense)}>
                          <Eye className="h-4 w-4 mr-2" />
                          View Details
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-2xl">
                        <DialogHeader>
                          <DialogTitle>Expense Details</DialogTitle>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <label className="text-sm font-medium text-gray-700">Title</label>
                              <p className="text-sm">{expense.title}</p>
                            </div>
                            <div>
                              <label className="text-sm font-medium text-gray-700">Amount</label>
                              <p className="text-sm font-semibold">{expense.amount} {expense.currency}</p>
                            </div>
                            <div>
                              <label className="text-sm font-medium text-gray-700">Employee</label>
                              <p className="text-sm">{expense.user_name}</p>
                            </div>
                            <div>
                              <label className="text-sm font-medium text-gray-700">Date</label>
                              <p className="text-sm">{new Date(expense.expense_date).toLocaleDateString()}</p>
                            </div>
                            <div>
                              <label className="text-sm font-medium text-gray-700">Status</label>
                              <div className="mt-1">{getStatusBadge(expense.status)}</div>
                            </div>
                            <div>
                              <label className="text-sm font-medium text-gray-700">Priority</label>
                              <div className="mt-1">{getPriorityBadge(expense.priority)}</div>
                            </div>
                          </div>
                          
                          {expense.description && (
                            <div>
                              <label className="text-sm font-medium text-gray-700">Description</label>
                              <p className="text-sm bg-gray-50 p-3 rounded-md mt-1">{expense.description}</p>
                            </div>
                          )}
                          
                          {expense.status === 'approved' && expense.approved_by_name && (
                            <div className="bg-green-50 border border-green-200 rounded-md p-3">
                              <div className="flex items-center gap-2 text-green-800">
                                <CheckCircle className="h-4 w-4" />
                                <span className="text-sm font-medium">
                                  Approved by {expense.approved_by_name} on {expense.approved_at ? new Date(expense.approved_at).toLocaleDateString() : 'N/A'}
                                </span>
                              </div>
                            </div>
                          )}
                          
                          {expense.status === 'rejected' && expense.rejection_reason && (
                            <div className="bg-red-50 border border-red-200 rounded-md p-3">
                              <div className="flex items-center gap-2 text-red-800">
                                <XCircle className="h-4 w-4" />
                                <span className="text-sm font-medium">Rejection Reason:</span>
                              </div>
                              <p className="text-sm text-red-700 mt-1">{expense.rejection_reason}</p>
                            </div>
                          )}
                        </div>
                      </DialogContent>
                    </Dialog>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {historyData?.pagination && historyData.pagination.total_pages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            Page {historyData.pagination.page} of {historyData.pagination.total_pages}
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePageChange(historyData.pagination.page - 1)}
              disabled={!historyData.pagination.has_previous}
            >
              <ChevronLeft className="h-4 w-4 mr-1" />
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePageChange(historyData.pagination.page + 1)}
              disabled={!historyData.pagination.has_next}
            >
              Next
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>
      )}

      {/* Export Dialog */}
      <Dialog open={exportDialogOpen} onOpenChange={setExportDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileSpreadsheet className="h-5 w-5" />
              Export Expense History
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Choose which expenses to export to Excel format:
            </p>
            <div className="grid gap-3">
              <Button
                onClick={() => exportToExcel('all')}
                variant="outline"
                className="justify-start h-12"
                disabled={exportLoading}
              >
                <FileText className="h-4 w-4 mr-3" />
                <div className="text-left">
                  <div className="font-medium">All Expenses</div>
                  <div className="text-sm text-gray-500">Export all expense records</div>
                </div>
              </Button>
              
              <Button
                onClick={() => exportToExcel('approved')}
                variant="outline"
                className="justify-start h-12"
                disabled={exportLoading}
              >
                <CheckCircle className="h-4 w-4 mr-3 text-green-600" />
                <div className="text-left">
                  <div className="font-medium">Approved Expenses</div>
                  <div className="text-sm text-gray-500">Export only approved expenses</div>
                </div>
              </Button>
              
              <Button
                onClick={() => exportToExcel('pending')}
                variant="outline"
                className="justify-start h-12"
                disabled={exportLoading}
              >
                <Clock className="h-4 w-4 mr-3 text-yellow-600" />
                <div className="text-left">
                  <div className="font-medium">Pending Expenses</div>
                  <div className="text-sm text-gray-500">Export only pending expenses</div>
                </div>
              </Button>
              
              <Button
                onClick={() => exportToExcel('rejected')}
                variant="outline"
                className="justify-start h-12"
                disabled={exportLoading}
              >
                <XCircle className="h-4 w-4 mr-3 text-red-600" />
                <div className="text-left">
                  <div className="font-medium">Rejected Expenses</div>
                  <div className="text-sm text-gray-500">Export only rejected expenses</div>
                </div>
              </Button>
            </div>
            
            {exportLoading && (
              <div className="flex items-center justify-center py-4">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <span className="ml-2 text-sm text-gray-600">Preparing export...</span>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ManagerHistory;
