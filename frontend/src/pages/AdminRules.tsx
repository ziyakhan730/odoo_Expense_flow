import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
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
  Plus,
  Edit,
  Trash2,
  Settings,
  DollarSign,
  Users,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle
} from "lucide-react";
import { useState, useEffect } from "react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { apiService } from "../services/api";

interface ApprovalRule {
  id: number;
  name: string;
  min_amount: number;
  max_amount: number | null;
  sequence: string[];
  percentage_required: number;
  admin_override: boolean;
  urgent_bypass: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const AdminRules = () => {
  const [rules, setRules] = useState<ApprovalRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [editingRule, setEditingRule] = useState<ApprovalRule | null>(null);
  const [deletingRule, setDeletingRule] = useState<ApprovalRule | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    min_amount: '',
    max_amount: '',
    sequence: [] as string[],
    percentage_required: 100,
    admin_override: true,
    urgent_bypass: true,
    is_active: true
  });

  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    try {
      setLoading(true);
      setError(null);
      const rulesData = await apiService.getApprovalRules();
      setRules(rulesData);
    } catch (err: any) {
      console.error('Error loading rules:', err);
      setError(err.message || 'Failed to load approval rules');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const ruleData = {
        ...formData,
        min_amount: parseFloat(formData.min_amount),
        max_amount: formData.max_amount ? parseFloat(formData.max_amount) : null,
      };
      
      await apiService.createApprovalRule(ruleData);
      toast.success('Approval rule created successfully');
      setShowCreateDialog(false);
      resetForm();
      loadRules();
    } catch (err: any) {
      console.error('Error creating rule:', err);
      toast.error('Failed to create approval rule: ' + err.message);
    }
  };

  const handleEditRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingRule) return;
    
    try {
      const ruleData = {
        ...formData,
        min_amount: parseFloat(formData.min_amount),
        max_amount: formData.max_amount ? parseFloat(formData.max_amount) : null,
      };
      
      await apiService.updateApprovalRule(editingRule.id, ruleData);
      toast.success('Approval rule updated successfully');
      setShowEditDialog(false);
      setEditingRule(null);
      resetForm();
      loadRules();
    } catch (err: any) {
      console.error('Error updating rule:', err);
      toast.error('Failed to update approval rule: ' + err.message);
    }
  };

  const handleDeleteRule = async () => {
    if (!deletingRule) return;
    
    try {
      await apiService.deleteApprovalRule(deletingRule.id);
      toast.success('Approval rule deleted successfully');
      setDeletingRule(null);
      loadRules();
    } catch (err: any) {
      console.error('Error deleting rule:', err);
      toast.error('Failed to delete approval rule: ' + err.message);
    }
  };

  const handleSetupDefaultRules = async () => {
    try {
      await apiService.setupDefaultRules();
      toast.success('Default approval rules created successfully');
      loadRules();
    } catch (err: any) {
      console.error('Error setting up default rules:', err);
      toast.error('Failed to setup default rules: ' + err.message);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      min_amount: '',
      max_amount: '',
      sequence: [],
      percentage_required: 100,
      admin_override: true,
      urgent_bypass: true,
      is_active: true
    });
  };

  const openEditDialog = (rule: ApprovalRule) => {
    setEditingRule(rule);
    setFormData({
      name: rule.name,
      min_amount: rule.min_amount.toString(),
      max_amount: rule.max_amount?.toString() || '',
      sequence: rule.sequence,
      percentage_required: rule.percentage_required,
      admin_override: rule.admin_override,
      urgent_bypass: rule.urgent_bypass,
      is_active: rule.is_active
    });
    setShowEditDialog(true);
  };

  const getSequenceDisplay = (sequence: string[]) => {
    return sequence.map(role => {
      switch (role) {
        case 'manager': return 'Manager';
        case 'admin': return 'Admin';
        default: return role;
      }
    }).join(' → ');
  };

  const getAmountRangeDisplay = (rule: ApprovalRule) => {
    if (rule.max_amount) {
      return `$${rule.min_amount.toLocaleString()} - $${rule.max_amount.toLocaleString()}`;
    } else {
      return `$${rule.min_amount.toLocaleString()}+`;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading approval rules...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={loadRules}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Approval Rules</h1>
          <p className="text-muted-foreground">Manage expense approval workflows and thresholds</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleSetupDefaultRules}>
            <Settings className="h-4 w-4 mr-2" />
            Setup Default Rules
          </Button>
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Rule
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create Approval Rule</DialogTitle>
                <DialogDescription>Define a new approval workflow rule</DialogDescription>
              </DialogHeader>
              <form onSubmit={handleCreateRule} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="rule-name">Rule Name</Label>
                    <Input
                      id="rule-name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="e.g., High Amount Approval"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="percentage">Approval Percentage</Label>
                    <Input
                      id="percentage"
                      type="number"
                      min="1"
                      max="100"
                      value={formData.percentage_required}
                      onChange={(e) => setFormData({ ...formData, percentage_required: parseInt(e.target.value) })}
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="min-amount">Minimum Amount ($)</Label>
                    <Input
                      id="min-amount"
                      type="number"
                      step="0.01"
                      value={formData.min_amount}
                      onChange={(e) => setFormData({ ...formData, min_amount: e.target.value })}
                      placeholder="0.00"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="max-amount">Maximum Amount ($)</Label>
                    <Input
                      id="max-amount"
                      type="number"
                      step="0.01"
                      value={formData.max_amount}
                      onChange={(e) => setFormData({ ...formData, max_amount: e.target.value })}
                      placeholder="Leave empty for unlimited"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Approval Sequence</Label>
                  <div className="flex gap-2">
                    <Select
                      value={formData.sequence[0] || ''}
                      onValueChange={(value) => setFormData({ ...formData, sequence: [value] })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="First approver" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="manager">Manager</SelectItem>
                        <SelectItem value="admin">Admin</SelectItem>
                      </SelectContent>
                    </Select>
                    {formData.sequence[0] && (
                      <Select
                        value={formData.sequence[1] || ''}
                        onValueChange={(value) => setFormData({ ...formData, sequence: [formData.sequence[0], value] })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Second approver" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="manager">Manager</SelectItem>
                          <SelectItem value="admin">Admin</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="admin-override"
                      checked={formData.admin_override}
                      onCheckedChange={(checked) => setFormData({ ...formData, admin_override: checked })}
                    />
                    <Label htmlFor="admin-override">Admin Override</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="urgent-bypass"
                      checked={formData.urgent_bypass}
                      onCheckedChange={(checked) => setFormData({ ...formData, urgent_bypass: checked })}
                    />
                    <Label htmlFor="urgent-bypass">Urgent Bypass</Label>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    id="is-active"
                    checked={formData.is_active}
                    onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
                  />
                  <Label htmlFor="is-active">Active</Label>
                </div>

                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                    Cancel
                  </Button>
                  <Button type="submit">Create Rule</Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Rules List */}
      <div className="grid gap-4">
        {rules.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <Settings className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-semibold mb-2">No Approval Rules</h3>
              <p className="text-muted-foreground mb-4">Create your first approval rule or setup default rules.</p>
              <Button onClick={handleSetupDefaultRules} variant="outline">
                <Settings className="h-4 w-4 mr-2" />
                Setup Default Rules
              </Button>
            </CardContent>
          </Card>
        ) : (
          rules.map((rule) => (
            <Card key={rule.id} className={cn(
              "transition-all duration-200 hover:shadow-md",
              !rule.is_active && "opacity-60"
            )}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <CardTitle className="text-lg">{rule.name}</CardTitle>
                    <Badge variant={rule.is_active ? "default" : "secondary"}>
                      {rule.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => openEditDialog(rule)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Delete Approval Rule</AlertDialogTitle>
                          <AlertDialogDescription>
                            Are you sure you want to delete "{rule.name}"? This action cannot be undone.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction
                            onClick={() => {
                              setDeletingRule(rule);
                              handleDeleteRule();
                            }}
                            className="bg-red-600 hover:bg-red-700"
                          >
                            Delete
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <DollarSign className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm font-medium">Amount Range</span>
                    </div>
                    <p className="text-lg font-semibold">{getAmountRangeDisplay(rule)}</p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm font-medium">Approval Sequence</span>
                    </div>
                    <p className="text-sm">{getSequenceDisplay(rule.sequence)}</p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm font-medium">Requirements</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      <Badge variant="outline" className="text-xs">
                        {rule.percentage_required}% approval
                      </Badge>
                      {rule.admin_override && (
                        <Badge variant="outline" className="text-xs">
                          Admin Override
                        </Badge>
                      )}
                      {rule.urgent_bypass && (
                        <Badge variant="outline" className="text-xs">
                          Urgent Bypass
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Edit Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Approval Rule</DialogTitle>
            <DialogDescription>Update the approval workflow rule</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleEditRule} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-rule-name">Rule Name</Label>
                <Input
                  id="edit-rule-name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., High Amount Approval"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-percentage">Approval Percentage</Label>
                <Input
                  id="edit-percentage"
                  type="number"
                  min="1"
                  max="100"
                  value={formData.percentage_required}
                  onChange={(e) => setFormData({ ...formData, percentage_required: parseInt(e.target.value) })}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-min-amount">Minimum Amount ($)</Label>
                <Input
                  id="edit-min-amount"
                  type="number"
                  step="0.01"
                  value={formData.min_amount}
                  onChange={(e) => setFormData({ ...formData, min_amount: e.target.value })}
                  placeholder="0.00"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-max-amount">Maximum Amount ($)</Label>
                <Input
                  id="edit-max-amount"
                  type="number"
                  step="0.01"
                  value={formData.max_amount}
                  onChange={(e) => setFormData({ ...formData, max_amount: e.target.value })}
                  placeholder="Leave empty for unlimited"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Approval Sequence</Label>
              <div className="flex gap-2">
                <Select
                  value={formData.sequence[0] || ''}
                  onValueChange={(value) => setFormData({ ...formData, sequence: [value] })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="First approver" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="manager">Manager</SelectItem>
                    <SelectItem value="admin">Admin</SelectItem>
                  </SelectContent>
                </Select>
                {formData.sequence[0] && (
                  <Select
                    value={formData.sequence[1] || ''}
                    onValueChange={(value) => setFormData({ ...formData, sequence: [formData.sequence[0], value] })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Second approver" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="manager">Manager</SelectItem>
                      <SelectItem value="admin">Admin</SelectItem>
                    </SelectContent>
                  </Select>
                )}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center space-x-2">
                <Switch
                  id="edit-admin-override"
                  checked={formData.admin_override}
                  onCheckedChange={(checked) => setFormData({ ...formData, admin_override: checked })}
                />
                <Label htmlFor="edit-admin-override">Admin Override</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="edit-urgent-bypass"
                  checked={formData.urgent_bypass}
                  onCheckedChange={(checked) => setFormData({ ...formData, urgent_bypass: checked })}
                />
                <Label htmlFor="edit-urgent-bypass">Urgent Bypass</Label>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="edit-is-active"
                checked={formData.is_active}
                onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
              />
              <Label htmlFor="edit-is-active">Active</Label>
            </div>

            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => setShowEditDialog(false)}>
                Cancel
              </Button>
              <Button type="submit">Update Rule</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AdminRules;
