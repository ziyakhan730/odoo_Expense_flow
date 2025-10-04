import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { 
  Upload, 
  Eye, 
  X, 
  Loader2,
  CheckCircle2,
  AlertCircle,
  DollarSign,
  Calendar,
  Tag,
  FileText,
  Camera
} from "lucide-react";
import { toast } from "sonner";
import { apiService } from "@/services/api";

interface Country {
  name: {
    common: string;
    official: string;
  };
  currencies: Record<string, {
    name: string;
    symbol: string;
  }>;
}

interface Currency {
  code: string;
  name: string;
  symbol: string;
  country: string;
}

interface ExchangeRates {
  rates: Record<string, number>;
  base: string;
  date: string;
}

interface OCRData {
  text: string;
  confidence: number;
  extracted_data: {
    amount?: number;
    merchant?: string;
    date?: string;
    items?: string[];
  };
  merchant_info?: {
    name?: string;
    address?: string;
    phone?: string;
  };
}

interface ExpenseCategory {
  id: number;
  name: string;
  description?: string;
}

const ExpenseSubmission = () => {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    amount: "",
    currency: "USD",
    expense_date: "",
    category_id: "",
    priority: "medium",
    tags: "",
    notes: ""
  });

  const [receiptFile, setReceiptFile] = useState<File | null>(null);
  const [receiptPreview, setReceiptPreview] = useState<string | null>(null);
  const [ocrData, setOcrData] = useState<OCRData | null>(null);
  const [showOcrModal, setShowOcrModal] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Data states
  const [countries, setCountries] = useState<Country[]>([]);
  const [currencies, setCurrencies] = useState<Currency[]>([]);
  const [exchangeRates, setExchangeRates] = useState<ExchangeRates | null>(null);
  const [categories, setCategories] = useState<ExpenseCategory[]>([]);

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [countriesData, exchangeRatesData, categoriesData] = await Promise.all([
        apiService.getCountriesCurrencies(),
        apiService.getExchangeRates(),
        apiService.getExpenseCategories()
      ]);

      setCountries(countriesData);
      setExchangeRates(exchangeRatesData);
      
      // Filter only active categories
      // Fix: Add 'is_active' to ExpenseCategory type and use type assertion for safety
      const activeCategories = categoriesData.filter(
        (cat: ExpenseCategory & { is_active?: boolean }) => cat.is_active !== false
      );
      setCategories(activeCategories);

      // Process currencies from countries data
      const processedCurrencies: Currency[] = [];
      countriesData.forEach((country: Country) => {
        Object.entries(country.currencies).forEach(([code, currency]) => {
          if (!processedCurrencies.find(c => c.code === code)) {
            processedCurrencies.push({
              code,
              name: currency.name,
              symbol: currency.symbol,
              country: country.name.common
            });
          }
        });
      });
      setCurrencies(processedCurrencies.sort((a, b) => a.code.localeCompare(b.code)));

    } catch (error) {
      console.error('Error loading initial data:', error);
      toast.error('Failed to load initial data');
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setReceiptFile(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setReceiptPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const processReceiptOCR = async () => {
    if (!receiptFile) return;

    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('file', receiptFile);

      console.log('Sending OCR request with file:', {
        name: receiptFile.name,
        size: receiptFile.size,
        type: receiptFile.type
      });

      const ocrResult = await apiService.processReceiptOCR(formData);
      console.log('OCR result:', ocrResult);
      
      setOcrData(ocrResult);
      setShowOcrModal(true);

      // Auto-fill form with OCR data
      if (ocrResult.extracted_data) {
        const extracted = ocrResult.extracted_data;
        setFormData(prev => ({
          ...prev,
          title: extracted.merchant || prev.title,
          amount: extracted.amount?.toString() || prev.amount,
          expense_date: extracted.date || prev.expense_date,
          description: extracted.items?.join(', ') || prev.description
        }));
      }

      toast.success('Receipt processed successfully!');
    } catch (error: any) {
      console.error('OCR processing error:', error);
      toast.error(error.message || 'Failed to process receipt');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const submitData = {
        ...formData,
        amount: parseFloat(formData.amount),
        category_id: formData.category_id ? parseInt(formData.category_id) : undefined,
        tags: formData.tags ? formData.tags.split(',').map(tag => tag.trim()) : []
      };

      const formDataToSend = new FormData();
      Object.entries(submitData).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          if (key === 'tags' && Array.isArray(value)) {
            formDataToSend.append(key, JSON.stringify(value));
          } else {
            formDataToSend.append(key, value.toString());
          }
        }
      });

      if (receiptFile) {
        formDataToSend.append('receipt_file', receiptFile);
      }

      await apiService.createExpense(formDataToSend);
      
      toast.success('Expense submitted successfully!');
      
      // Reset form
      setFormData({
        title: "",
        description: "",
        amount: "",
        currency: "USD",
        expense_date: "",
        category_id: "",
        priority: "medium",
        tags: "",
        notes: ""
      });
      setReceiptFile(null);
      setReceiptPreview(null);
      setOcrData(null);

    } catch (error: any) {
      console.error('Expense submission error:', error);
      toast.error(error.message || 'Failed to submit expense');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getCurrencyDisplay = (currency: Currency) => {
    return `${currency.code} - ${currency.name} (${currency.symbol})`;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Submit New Expense</h1>
          <p className="text-muted-foreground">Fill in the details and upload your receipt</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Expense Details</CardTitle>
          <CardDescription>Enter the expense information below</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="title">Title *</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  placeholder="Expense title"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="amount">Amount *</Label>
                <Input
                  id="amount"
                  type="number"
                  step="0.01"
                  value={formData.amount}
                  onChange={(e) => setFormData({...formData, amount: e.target.value})}
                  placeholder="0.00"
                  required
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="currency">Currency *</Label>
                <Select
                  value={formData.currency}
                  onValueChange={(value) => setFormData({...formData, currency: value})}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select currency" />
                  </SelectTrigger>
                  <SelectContent>
                    {currencies.map((currency) => (
                      <SelectItem key={currency.code} value={currency.code}>
                        {getCurrencyDisplay(currency)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="expense_date">Date *</Label>
                <Input
                  id="expense_date"
                  type="date"
                  value={formData.expense_date}
                  onChange={(e) => setFormData({...formData, expense_date: e.target.value})}
                  required
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <Select
                  value={formData.category_id}
                  onValueChange={(value) => setFormData({...formData, category_id: value})}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem key={category.id} value={category.id.toString()}>
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="priority">Priority</Label>
                <Select
                  value={formData.priority}
                  onValueChange={(value) => setFormData({...formData, priority: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="urgent">Urgent</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="Brief description of the expense"
                rows={3}
              />
            </div>

            {/* Receipt Upload Section */}
            <div className="space-y-4">
              <Label htmlFor="receipt">Receipt Upload (OCR enabled)</Label>
              <div className="border-2 border-dashed border-border rounded-lg p-6">
                <div className="flex flex-col items-center space-y-4">
                  <Camera className="h-12 w-12 text-muted-foreground" />
                  <div className="text-center">
                    <p className="text-sm font-medium">Upload your receipt</p>
                    <p className="text-xs text-muted-foreground">
                      Our AI will auto-fill the details from your receipt
                    </p>
                  </div>
                  
                  <div className="flex gap-2">
                    <Input
                      id="receipt"
                      type="file"
                      accept="image/*"
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => document.getElementById('receipt')?.click()}
                    >
                      <Upload className="mr-2 h-4 w-4" />
                      Choose File
                    </Button>
                    {receiptFile && (
                      <Button
                        type="button"
                        variant="outline"
                        onClick={processReceiptOCR}
                        disabled={isProcessing}
                      >
                        {isProcessing ? (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        ) : (
                          <Eye className="mr-2 h-4 w-4" />
                        )}
                        Process OCR
                      </Button>
                    )}
                  </div>

                  {receiptFile && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <FileText className="h-4 w-4" />
                      <span>{receiptFile.name}</span>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setReceiptFile(null);
                          setReceiptPreview(null);
                        }}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  )}

                  {receiptPreview && (
                    <div className="mt-4">
                      <img
                        src={receiptPreview}
                        alt="Receipt preview"
                        className="max-w-xs max-h-48 object-contain rounded border"
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Additional Information */}
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="tags">Tags</Label>
                <Input
                  id="tags"
                  value={formData.tags}
                  onChange={(e) => setFormData({...formData, tags: e.target.value})}
                  placeholder="travel, client, urgent (comma separated)"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="notes">Notes</Label>
                <Input
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({...formData, notes: e.target.value})}
                  placeholder="Additional notes"
                />
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex gap-2 pt-4">
              <Button type="submit" disabled={isSubmitting} className="flex-1">
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="mr-2 h-4 w-4" />
                    Submit Expense
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* OCR Results Modal */}
      <Dialog open={showOcrModal} onOpenChange={setShowOcrModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>OCR Results</DialogTitle>
            <DialogDescription>
              Review the extracted information from your receipt
            </DialogDescription>
          </DialogHeader>
          
          {ocrData && (
            <div className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold mb-2">Confidence Score</h4>
                  <Badge variant={ocrData.confidence > 0.8 ? "default" : "secondary"}>
                    {(ocrData.confidence * 100).toFixed(1)}%
                  </Badge>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Extracted Data</h4>
                  <div className="space-y-1 text-sm">
                    {ocrData.extracted_data.amount && (
                      <p><strong>Amount:</strong> {ocrData.extracted_data.amount}</p>
                    )}
                    {ocrData.extracted_data.merchant && (
                      <p><strong>Merchant:</strong> {ocrData.extracted_data.merchant}</p>
                    )}
                    {ocrData.extracted_data.date && (
                      <p><strong>Date:</strong> {ocrData.extracted_data.date}</p>
                    )}
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Raw OCR Text</h4>
                <div className="bg-muted p-3 rounded text-sm max-h-32 overflow-y-auto">
                  {ocrData.text}
                </div>
              </div>

              {ocrData.merchant_info && (
                <div>
                  <h4 className="font-semibold mb-2">Merchant Information</h4>
                  <div className="bg-muted p-3 rounded text-sm">
                    {ocrData.merchant_info.name && <p><strong>Name:</strong> {ocrData.merchant_info.name}</p>}
                    {ocrData.merchant_info.address && <p><strong>Address:</strong> {ocrData.merchant_info.address}</p>}
                    {ocrData.merchant_info.phone && <p><strong>Phone:</strong> {ocrData.merchant_info.phone}</p>}
                  </div>
                </div>
              )}

              <div className="flex gap-2">
                <Button onClick={() => setShowOcrModal(false)}>
                  Close
                </Button>
                <Button variant="outline" onClick={() => {
                  // Auto-fill form with OCR data
                  if (ocrData.extracted_data) {
                    const extracted = ocrData.extracted_data;
                    setFormData(prev => ({
                      ...prev,
                      title: extracted.merchant || prev.title,
                      amount: extracted.amount?.toString() || prev.amount,
                      expense_date: extracted.date || prev.expense_date,
                      description: extracted.items?.join(', ') || prev.description
                    }));
                  }
                  setShowOcrModal(false);
                  toast.success('Form auto-filled with OCR data!');
                }}>
                  Use This Data
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ExpenseSubmission;
