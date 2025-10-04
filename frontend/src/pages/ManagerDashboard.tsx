import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Textarea } from '../components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Alert, AlertDescription } from '../components/ui/alert';
import { apiService } from '../services/api';
import { CheckCircle, XCircle, Eye, Clock, DollarSign, Calendar, User, FileText, LayoutDashboard, History } from 'lucide-react';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Routes, Route } from 'react-router-dom';

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

const navItems = [
  { label: "Dashboard", path: "/manager", icon: LayoutDashboard },
  { label: "Approvals", path: "/manager/approvals", icon: CheckCircle },
  { label: "History", path: "/manager/history", icon: History },
];

const ManagerOverview: React.FC = () => {
  const [pendingCount, setPendingCount] = useState(0);
  const [approvedCount, setApprovedCount] = useState(0);
  const [rejectedCount, setRejectedCount] = useState(0);
  const [approvedTodayCount, setApprovedTodayCount] = useState(0);
  const [teamMembersCount, setTeamMembersCount] = useState(0);
  const [totalExpenses, setTotalExpenses] = useState(0);
  const [recentApprovals, setRecentApprovals] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load dashboard data from the new API endpoint
      const dashboardData = await apiService.getManagerDashboardData();
      
      setPendingCount(dashboardData.pending_count);
      setApprovedCount(dashboardData.approved_count);
      setRejectedCount(dashboardData.rejected_count);
      setApprovedTodayCount(dashboardData.today_approvals);
      setTeamMembersCount(dashboardData.team_members_count);
      setTotalExpenses(dashboardData.total_expenses);
      setRecentApprovals(dashboardData.recent_approvals);
      
      setError(null);
    } catch (err: any) {
      console.error('Error loading dashboard data:', err);
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
      <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Manager Dashboard</h1>
          <p className="text-gray-600">Manage your team's expense approvals</p>
        </div>
        <Button onClick={loadDashboardData} variant="outline">
          Refresh
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{pendingCount}</div>
            <p className="text-xs text-muted-foreground">Awaiting your review</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Approved Today</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{approvedTodayCount}</div>
            <p className="text-xs text-muted-foreground">Expenses approved today</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Approved</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{approvedCount}</div>
            <p className="text-xs text-muted-foreground">All time approved</p>
          </CardContent>
        </Card>
        
        <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Team Members</CardTitle>
            <User className="h-4 w-4 text-blue-600" />
                </CardHeader>
                <CardContent>
            <div className="text-2xl font-bold">{teamMembersCount}</div>
            <p className="text-xs text-muted-foreground">In your set</p>
                </CardContent>
              </Card>
        </div>

      {/* Additional Statistics */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Expenses</CardTitle>
            <FileText className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalExpenses}</div>
            <p className="text-xs text-muted-foreground">All submitted expenses</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Rejected</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{rejectedCount}</div>
            <p className="text-xs text-muted-foreground">Rejected expenses</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Approval Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {totalExpenses > 0 ? Math.round((approvedCount / totalExpenses) * 100) : 0}%
            </div>
            <p className="text-xs text-muted-foreground">Success rate</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity and Pending Approvals */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Recent Approvals */}
        {recentApprovals.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Recent Approvals</CardTitle>
              <p className="text-sm text-muted-foreground">Latest approved expenses from your team</p>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
                {recentApprovals.map((expense) => (
                <div
                  key={expense.id}
                    className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-accent/50 transition-colors"
                  >
                    <div className="space-y-1">
                      <p className="font-medium">{expense.title}</p>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <span>{expense.user_name}</span>
                        <span>•</span>
                        <span>{new Date(expense.expense_date).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="font-bold">
                          {expense.amount} {expense.currency}
                        </p>
                      </div>
                      {getStatusBadge(expense.status)}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <p className="text-sm text-muted-foreground">Manage your team's expenses</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button 
              className="w-full justify-start" 
              variant="outline"
              onClick={() => window.location.href = '/manager/approvals'}
            >
              <Clock className="h-4 w-4 mr-2" />
              Review Pending Approvals ({pendingCount})
            </Button>
            
            <Button 
              className="w-full justify-start" 
              variant="outline"
              onClick={() => window.location.href = '/manager/history'}
            >
              <History className="h-4 w-4 mr-2" />
              View Approval History
            </Button>
            
            {pendingCount > 0 && (
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                <div className="flex items-center gap-2 text-yellow-800">
                  <Clock className="h-4 w-4" />
                  <span className="text-sm font-medium">
                    {pendingCount} expense{pendingCount !== 1 ? 's' : ''} awaiting your review
                  </span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

const ExpenseApprovals: React.FC = () => {
  const [pendingExpenses, setPendingExpenses] = useState<Expense[]>([]);
  const [selectedExpense, setSelectedExpense] = useState<Expense | null>(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  useEffect(() => {
    loadPendingApprovals();
  }, []);

  const loadPendingApprovals = async () => {
    try {
      setLoading(true);
      const data = await apiService.getPendingApprovals();
      setPendingExpenses(data);
      setError(null);
    } catch (err: any) {
      console.error('Error loading pending approvals:', err);
      setError(err.message || 'Failed to load pending approvals');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (expenseId: number) => {
    try {
      setActionLoading(expenseId);
      await apiService.approveExpense(expenseId);
      await loadPendingApprovals(); // Refresh the list
      setSelectedExpense(null);
    } catch (err: any) {
      console.error('Error approving expense:', err);
      setError(err.message || 'Failed to approve expense');
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (expenseId: number) => {
    if (!rejectionReason.trim()) {
      setError('Please provide a reason for rejection');
      return;
    }

    try {
      setActionLoading(expenseId);
      await apiService.rejectExpense(expenseId, rejectionReason);
      await loadPendingApprovals(); // Refresh the list
      setSelectedExpense(null);
      setRejectionReason('');
    } catch (err: any) {
      console.error('Error rejecting expense:', err);
      setError(err.message || 'Failed to reject expense');
    } finally {
      setActionLoading(null);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: { variant: 'secondary' as const, icon: Clock, text: 'Pending' },
      approved: { variant: 'default' as const, icon: CheckCircle, text: 'Approved' },
      rejected: { variant: 'destructive' as const, icon: XCircle, text: 'Rejected' },
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;
    const Icon = config.icon;
    
    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Expense Approvals</h1>
          <p className="text-gray-600">Review and approve expenses from your team</p>
        </div>
        <Button onClick={loadPendingApprovals} variant="outline">
          Refresh
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {pendingExpenses.length === 0 ? (
        <Card>
          <CardContent className="text-center py-8">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Pending Approvals</h3>
            <p className="text-gray-600">All expenses from your team have been reviewed.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {pendingExpenses.map((expense) => (
            <Card key={expense.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <CardTitle className="text-lg">{expense.title}</CardTitle>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <User className="h-4 w-4" />
                      {expense.user_name}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(expense.status)}
                    {getPriorityBadge(expense.priority)}
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <DollarSign className="h-4 w-4 text-green-600" />
                    <span className="font-medium">{expense.amount} {expense.currency}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-blue-600" />
                    <span>{new Date(expense.expense_date).toLocaleDateString()}</span>
                  </div>
                  {expense.category && (
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-purple-600" />
                      <span>{expense.category.name}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-orange-600" />
                    <span>Submitted {new Date(expense.submission_date).toLocaleDateString()}</span>
                  </div>
                    </div>

                {expense.description && (
                  <div className="bg-gray-50 p-3 rounded-md">
                    <p className="text-sm text-gray-700">{expense.description}</p>
                  </div>
                )}

                    <div className="flex gap-2">
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
                          {expense.category && (
                            <div>
                              <label className="text-sm font-medium text-gray-700">Category</label>
                              <p className="text-sm">{expense.category.name}</p>
                            </div>
                          )}
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

                        <div className="flex gap-2 pt-4">
                          <Button
                            onClick={() => handleApprove(expense.id)}
                            disabled={actionLoading === expense.id}
                            className="flex-1"
                          >
                            {actionLoading === expense.id ? (
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                            ) : (
                            <CheckCircle className="h-4 w-4 mr-2" />
                            )}
                            Approve
                          </Button>
                          
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button variant="destructive" className="flex-1">
                                <XCircle className="h-4 w-4 mr-2" />
                                Reject
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                                <DialogTitle>Reject Expense</DialogTitle>
                          </DialogHeader>
                          <div className="space-y-4">
                                <div>
                                  <label className="text-sm font-medium text-gray-700">Reason for Rejection</label>
                                  <Textarea
                                    value={rejectionReason}
                                    onChange={(e) => setRejectionReason(e.target.value)}
                                    placeholder="Please provide a reason for rejecting this expense..."
                                    className="mt-1"
                                  />
                            </div>
                                <div className="flex gap-2">
                                  <Button
                                    onClick={() => handleReject(expense.id)}
                                    disabled={actionLoading === expense.id || !rejectionReason.trim()}
                                    variant="destructive"
                                    className="flex-1"
                                  >
                                    {actionLoading === expense.id ? (
                                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                    ) : null}
                                    Confirm Rejection
                              </Button>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>
                  </div>
                    </DialogContent>
                  </Dialog>
            </div>
          </CardContent>
        </Card>
          ))}
                </div>
      )}
                </div>
  );
};

const ManagerDashboard: React.FC = () => {
  return (
    <DashboardLayout role="manager" navItems={navItems}>
      <Routes>
        <Route path="/" element={<ManagerOverview />} />
        <Route path="/approvals" element={<ExpenseApprovals />} />
        <Route path="/history" element={<div>Approval History - Coming Soon</div>} />
      </Routes>
    </DashboardLayout>
  );
};

export default ManagerDashboard;