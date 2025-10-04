import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Alert, AlertDescription } from '../components/ui/alert';
import { CheckCircle, XCircle, Clock, DollarSign, Calendar, FileText, User, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';

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
  category?: {
    name: string;
  };
  approved_by_name?: string;
  approved_at?: string;
  rejection_reason?: string;
}

const EmployeeExpenses: React.FC = () => {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMyExpenses();
  }, []);

  const loadMyExpenses = async () => {
    try {
      setLoading(true);
      const data = await apiService.getMyExpenses();
      setExpenses(data);
      setError(null);
    } catch (err: any) {
      console.error('Error loading my expenses:', err);
      setError(err.message || 'Failed to load expenses');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: { variant: 'secondary' as const, icon: Clock, text: 'Pending Review', color: 'text-yellow-600' },
      approved: { variant: 'default' as const, icon: CheckCircle, text: 'Approved', color: 'text-green-600' },
      rejected: { variant: 'destructive' as const, icon: XCircle, text: 'Rejected', color: 'text-red-600' },
      under_review: { variant: 'secondary' as const, icon: AlertCircle, text: 'Under Review', color: 'text-blue-600' },
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

  const getStatusSummary = () => {
    const summary = expenses.reduce((acc, expense) => {
      acc[expense.status] = (acc[expense.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return summary;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading your expenses...</p>
        </div>
      </div>
    );
  }

  const statusSummary = getStatusSummary();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">My Expenses</h1>
          <p className="text-gray-600">Track the status of your submitted expenses</p>
        </div>
        <Button onClick={loadMyExpenses} variant="outline">
          Refresh
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Status Summary */}
      {Object.keys(statusSummary).length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(statusSummary).map(([status, count]) => (
            <Card key={status}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 capitalize">{status.replace('_', ' ')}</p>
                    <p className="text-2xl font-bold">{count}</p>
                  </div>
                  {status === 'approved' && <CheckCircle className="h-8 w-8 text-green-500" />}
                  {status === 'rejected' && <XCircle className="h-8 w-8 text-red-500" />}
                  {status === 'pending' && <Clock className="h-8 w-8 text-yellow-500" />}
                  {status === 'under_review' && <AlertCircle className="h-8 w-8 text-blue-500" />}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {expenses.length === 0 ? (
        <Card>
          <CardContent className="text-center py-8">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Expenses Found</h3>
            <p className="text-gray-600">You haven't submitted any expenses yet.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {expenses.map((expense) => (
            <Card key={expense.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <CardTitle className="text-lg">{expense.title}</CardTitle>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <DollarSign className="h-4 w-4" />
                        <span className="font-medium">{expense.amount} {expense.currency}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        <span>{new Date(expense.expense_date).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(expense.status)}
                    {getPriorityBadge(expense.priority)}
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-orange-600" />
                    <span>Submitted {new Date(expense.submission_date).toLocaleDateString()}</span>
                  </div>
                  {expense.category && (
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-purple-600" />
                      <span>{expense.category.name}</span>
                    </div>
                  )}
                  {expense.approved_by_name && (
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4 text-green-600" />
                      <span>Approved by {expense.approved_by_name}</span>
                    </div>
                  )}
                </div>

                {expense.description && (
                  <div className="bg-gray-50 p-3 rounded-md">
                    <p className="text-sm text-gray-700">{expense.description}</p>
                  </div>
                )}

                {expense.status === 'rejected' && expense.rejection_reason && (
                  <Alert variant="destructive">
                    <XCircle className="h-4 w-4" />
                    <AlertDescription>
                      <strong>Rejection Reason:</strong> {expense.rejection_reason}
                    </AlertDescription>
                  </Alert>
                )}

                {expense.status === 'approved' && expense.approved_at && (
                  <div className="bg-green-50 border border-green-200 rounded-md p-3">
                    <div className="flex items-center gap-2 text-green-800">
                      <CheckCircle className="h-4 w-4" />
                      <span className="text-sm font-medium">
                        Approved on {new Date(expense.approved_at).toLocaleDateString()}
                        {expense.approved_by_name && ` by ${expense.approved_by_name}`}
                      </span>
                    </div>
                  </div>
                )}

                {expense.status === 'pending' && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
                    <div className="flex items-center gap-2 text-yellow-800">
                      <Clock className="h-4 w-4" />
                      <span className="text-sm font-medium">
                        Waiting for manager approval
                      </span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default EmployeeExpenses;
