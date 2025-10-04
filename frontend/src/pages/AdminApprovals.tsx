import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { 
  CheckCircle,
  XCircle,
  Clock,
  DollarSign,
  User,
  Calendar,
  FileText,
  AlertTriangle,
  Eye,
  Filter,
  Search,
  RefreshCw
} from "lucide-react";
import { useState, useEffect } from "react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { apiService } from "../services/api";

interface ApprovalExpense {
  id: number;
  title: string;
  description: string;
  amount: number;
  currency: string;
  converted_amount?: number;
  expense_date: string;
  submission_date: string;
  status: string;
  priority: string;
  urgent: boolean;
  current_stage: string;
  escalated: boolean;
  user_name: string;
  user_username: string;
  category_name?: string;
  approval_records: Array<{
    id: number;
    approver_name: string;
    approver_username: string;
    role: string;
    status: string;
    comment?: string;
    approved_at?: string;
    created_at: string;
  }>;
  approval_rule_name?: string;
  next_approver: string;
  approval_percentage: number;
}

const AdminApprovals = () => {
  const [expenses, setExpenses] = useState<ApprovalExpense[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedExpense, setSelectedExpense] = useState<ApprovalExpense | null>(null);
  const [showApprovalDialog, setShowApprovalDialog] = useState(false);
  const [showRejectionDialog, setShowRejectionDialog] = useState(false);
  const [actionType, setActionType] = useState<'approve' | 'reject' | null>(null);
  const [comment, setComment] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    priority: 'all',
    urgent: 'all',
    search: ''
  });

  useEffect(() => {
    loadApprovals();
  }, []);

  const loadApprovals = async () => {
    try {
      setLoading(true);
      setError(null);
      const expensesData = await apiService.getPendingApprovalsWorkflow();
      setExpenses(expensesData);
    } catch (err: any) {
      console.error('Error loading approvals:', err);
      setError(err.message || 'Failed to load pending approvals');
    } finally {
      setLoading(false);
    }
  };

  const handleApproval = async (expenseId: number, action: 'approve' | 'reject') => {
    try {
      if (action === 'approve') {
        await apiService.approveExpenseWorkflow(expenseId, { comment });
        toast.success('Expense approved successfully');
      } else {
        await apiService.rejectExpenseWorkflow(expenseId, { comment });
        toast.success('Expense rejected successfully');
      }
      
      setShowApprovalDialog(false);
      setShowRejectionDialog(false);
      setComment('');
      setSelectedExpense(null);
      loadApprovals();
    } catch (err: any) {
      console.error(`Error ${action}ing expense:`, err);
      toast.error(`Failed to ${action} expense: ${err.message}`);
    }
  };

  const openApprovalDialog = (expense: ApprovalExpense, action: 'approve' | 'reject') => {
    setSelectedExpense(expense);
    setActionType(action);
    setComment('');
    if (action === 'approve') {
      setShowApprovalDialog(true);
    } else {
      setShowRejectionDialog(true);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'text-green-600 bg-green-100';
      case 'rejected': return 'text-red-600 bg-red-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      case 'in_progress': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getFilteredExpenses = () => {
    return expenses.filter(expense => {
      if (filters.status !== 'all' && expense.status !== filters.status) return false;
      if (filters.priority !== 'all' && expense.priority !== filters.priority) return false;
      if (filters.urgent !== 'all') {
        if (filters.urgent === 'urgent' && !expense.urgent) return false;
        if (filters.urgent === 'normal' && expense.urgent) return false;
      }
      if (filters.search && !expense.title.toLowerCase().includes(filters.search.toLowerCase()) && 
          !expense.user_name.toLowerCase().includes(filters.search.toLowerCase())) return false;
      return true;
    });
  };

  const filteredExpenses = getFilteredExpenses();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading pending approvals...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={loadApprovals}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Approval Management</h1>
          <p className="text-muted-foreground">Review and approve expense submissions</p>
        </div>
        <Button onClick={loadApprovals} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label htmlFor="status-filter">Status</Label>
              <Select value={filters.status} onValueChange={(value) => setFilters({...filters, status: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="All Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="in_progress">In Progress</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="priority-filter">Priority</Label>
              <Select value={filters.priority} onValueChange={(value) => setFilters({...filters, priority: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="All Priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Priority</SelectItem>
                  <SelectItem value="urgent">Urgent</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="urgent-filter">Urgency</Label>
              <Select value={filters.urgent} onValueChange={(value) => setFilters({...filters, urgent: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="All Urgency" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Urgency</SelectItem>
                  <SelectItem value="urgent">Urgent Only</SelectItem>
                  <SelectItem value="normal">Normal Only</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="search">Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search"
                  placeholder="Search expenses..."
                  value={filters.search}
                  onChange={(e) => setFilters({...filters, search: e.target.value})}
                  className="pl-10"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Expenses List */}
      <div className="space-y-4">
        {filteredExpenses.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <FileText className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-semibold mb-2">No Expenses Found</h3>
              <p className="text-muted-foreground">
                {expenses.length === 0 
                  ? "No expenses are pending approval." 
                  : "No expenses match the current filters."
                }
              </p>
            </CardContent>
          </Card>
        ) : (
          filteredExpenses.map((expense) => (
            <Card key={expense.id} className={cn(
              "transition-all duration-200 hover:shadow-md",
              expense.urgent && "border-red-200 bg-red-50/50"
            )}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <CardTitle className="text-lg">{expense.title}</CardTitle>
                    {expense.urgent && (
                      <Badge variant="destructive" className="animate-pulse">
                        <AlertTriangle className="h-3 w-3 mr-1" />
                        URGENT
                      </Badge>
                    )}
                    <Badge className={getStatusColor(expense.status)}>
                      {expense.status.toUpperCase()}
                    </Badge>
                    <Badge className={getPriorityColor(expense.priority)}>
                      {expense.priority.toUpperCase()}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setSelectedExpense(expense)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    {expense.status === 'pending' && (
                      <>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openApprovalDialog(expense, 'approve')}
                          className="text-green-600 border-green-600 hover:bg-green-50"
                        >
                          <CheckCircle className="h-4 w-4 mr-1" />
                          Approve
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openApprovalDialog(expense, 'reject')}
                          className="text-red-600 border-red-600 hover:bg-red-50"
                        >
                          <XCircle className="h-4 w-4 mr-1" />
                          Reject
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <DollarSign className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm font-medium">Amount</span>
                    </div>
                    <p className="text-lg font-semibold">
                      {expense.currency} {expense.amount.toLocaleString()}
                    </p>
                    {expense.converted_amount && (
                      <p className="text-xs text-muted-foreground">
                        ≈ ${expense.converted_amount.toLocaleString()} USD
                      </p>
                    )}
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm font-medium">Employee</span>
                    </div>
                    <p className="text-sm font-medium">{expense.user_name}</p>
                    <p className="text-xs text-muted-foreground">@{expense.user_username}</p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm font-medium">Dates</span>
                    </div>
                    <p className="text-xs">Expense: {new Date(expense.expense_date).toLocaleDateString()}</p>
                    <p className="text-xs text-muted-foreground">
                      Submitted: {new Date(expense.submission_date).toLocaleDateString()}
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm font-medium">Workflow</span>
                    </div>
                    <p className="text-xs">Stage: {expense.current_stage}</p>
                    <p className="text-xs text-muted-foreground">
                      Next: {expense.next_approver}
                    </p>
                    {expense.escalated && (
                      <Badge variant="destructive" className="text-xs">
                        Escalated
                      </Badge>
                    )}
                  </div>
                </div>
                
                {expense.description && (
                  <div className="mt-4 pt-4 border-t">
                    <p className="text-sm text-muted-foreground">{expense.description}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Approval Dialog */}
      <Dialog open={showApprovalDialog} onOpenChange={setShowApprovalDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              Approve Expense
            </DialogTitle>
            <DialogDescription>
              Are you sure you want to approve this expense? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          {selectedExpense && (
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold">{selectedExpense.title}</h4>
                <p className="text-sm text-muted-foreground">
                  {selectedExpense.currency} {selectedExpense.amount.toLocaleString()} • {selectedExpense.user_name}
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="approval-comment">Approval Comment (Optional)</Label>
                <Textarea
                  id="approval-comment"
                  placeholder="Add a comment about this approval..."
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                />
              </div>
              
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowApprovalDialog(false)}>
                  Cancel
                </Button>
                <Button 
                  onClick={() => handleApproval(selectedExpense.id, 'approve')}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Approve Expense
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Rejection Dialog */}
      <Dialog open={showRejectionDialog} onOpenChange={setShowRejectionDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <XCircle className="h-5 w-5 text-red-600" />
              Reject Expense
            </DialogTitle>
            <DialogDescription>
              Please provide a reason for rejecting this expense.
            </DialogDescription>
          </DialogHeader>
          {selectedExpense && (
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold">{selectedExpense.title}</h4>
                <p className="text-sm text-muted-foreground">
                  {selectedExpense.currency} {selectedExpense.amount.toLocaleString()} • {selectedExpense.user_name}
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="rejection-comment">Rejection Reason *</Label>
                <Textarea
                  id="rejection-comment"
                  placeholder="Please provide a reason for rejection..."
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  required
                />
              </div>
              
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowRejectionDialog(false)}>
                  Cancel
                </Button>
                <Button 
                  onClick={() => handleApproval(selectedExpense.id, 'reject')}
                  disabled={!comment.trim()}
                  className="bg-red-600 hover:bg-red-700"
                >
                  <XCircle className="h-4 w-4 mr-2" />
                  Reject Expense
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AdminApprovals;
