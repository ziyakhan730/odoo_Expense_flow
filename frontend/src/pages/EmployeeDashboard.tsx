import DashboardLayout from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  LayoutDashboard, 
  Upload, 
  History, 
  User,
  DollarSign,
  Clock,
  CheckCircle2,
  XCircle
} from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Routes, Route } from "react-router-dom";
import ExpenseSubmission from "./ExpenseSubmission";
import EmployeeExpenses from "./EmployeeExpenses";

const navItems = [
  { label: "Dashboard", path: "/employee", icon: LayoutDashboard },
  { label: "Submit Expense", path: "/employee/submit", icon: Upload },
  { label: "History", path: "/employee/history", icon: History },
  { label: "Profile", path: "/employee/profile", icon: User },
];

const mockExpenses = [
  { id: 1, amount: 250, currency: "USD", category: "Travel", date: "2024-01-15", status: "approved", description: "Client meeting taxi" },
  { id: 2, amount: 1200, currency: "USD", category: "Hotel", date: "2024-01-14", status: "pending", description: "Conference accommodation" },
  { id: 3, amount: 85, currency: "USD", category: "Meals", date: "2024-01-13", status: "rejected", description: "Team lunch" },
  { id: 4, amount: 45, currency: "USD", category: "Office", date: "2024-01-12", status: "approved", description: "Office supplies" },
];

const EmployeeOverview = () => {

  const getStatusBadge = (status: string) => {
    const variants = {
      approved: "success" as const,
      rejected: "destructive" as const,
      pending: "warning" as const,
    };
    return <Badge variant={variants[status as keyof typeof variants]}>{status}</Badge>;
  };

  const stats = [
    { label: "Total Submitted", value: "$1,580", icon: DollarSign, color: "text-primary" },
    { label: "Pending", value: "$1,200", icon: Clock, color: "text-warning" },
    { label: "Approved", value: "$295", icon: CheckCircle2, color: "text-success" },
    { label: "Rejected", value: "$85", icon: XCircle, color: "text-destructive" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Employee Dashboard</h1>
          <p className="text-muted-foreground">Manage your expense claims</p>
        </div>
      </div>

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <Card key={stat.label}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">{stat.label}</CardTitle>
                  <Icon className={cn("h-4 w-4", stat.color)} />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stat.value}</div>
                </CardContent>
              </Card>
            );
          })}
        </div>


        {/* Expense History */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Expenses</CardTitle>
            <CardDescription>Your latest expense submissions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockExpenses.map((expense) => (
                <div
                  key={expense.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-accent/50 transition-colors"
                >
                  <div className="space-y-1">
                    <p className="font-medium">{expense.description}</p>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <span>{expense.category}</span>
                      <span>•</span>
                      <span>{expense.date}</span>
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
    </div>
  );
};

const EmployeeDashboard = () => {
  return (
    <DashboardLayout role="employee" navItems={navItems}>
      <Routes>
        <Route path="/" element={<EmployeeOverview />} />
        <Route path="/submit" element={<ExpenseSubmission />} />
        <Route path="/history" element={<EmployeeExpenses />} />
        <Route path="/profile" element={<div>Profile - Coming Soon</div>} />
      </Routes>
    </DashboardLayout>
  );
};

export default EmployeeDashboard;
