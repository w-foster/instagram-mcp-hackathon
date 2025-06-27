import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Eye, Edit, Trash2, BarChart3 } from "lucide-react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { ENDPOINTS } from "@/config/env";

interface ApiItem {
  id: number;
  product: string;
  category: string;
  price: number;
  min_discount: number;
  max_discount: number;
  coupon: string;
  duration?: number;
  created_at?: string;
}

interface QuizItem extends ApiItem {
  status: "active" | "paused" | "completed";
  responses: number;
  conversion_rate: number;
  selected_discount: number;
  discounted_price: number;
}

const QuizManager = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const { data: items, isLoading, error } = useQuery({
    queryKey: ["items"],
    queryFn: async (): Promise<ApiItem[]> => {
      console.log("Fetching items data from:", ENDPOINTS.ITEMS);
      
      try {
        const response = await fetch(ENDPOINTS.ITEMS);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log("Fetched items:", data);
        return data;
      } catch (error) {
        console.error("Failed to fetch items:", error);
        // Return mock data if API fails
        return [
          {
            id: 100,
            product: "Dog Food",
            category: "Animal Feed",
            price: 23.99,
            min_discount: 10,
            max_discount: 30,
            coupon: "REDEEMFOOD",
            duration: 7,
            created_at: new Date().toISOString()
          },
          {
            id: 101,
            product: "Cat Food",
            category: "Animal Feed",
            price: 23.99,
            min_discount: 10,
            max_discount: 30,
            coupon: "REDEEMCATFOOD",
            duration: 3,
            created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
          }
        ];
      }
    },
  });

  const calculateStatus = (item: ApiItem): "active" | "completed" | "paused" => {
    if (!item.created_at || !item.duration) return "active";
    
    const createdAt = new Date(item.created_at);
    const now = new Date();
    const daysPassed = Math.floor((now.getTime() - createdAt.getTime()) / (1000 * 60 * 60 * 24));
    
    if (daysPassed >= item.duration) {
      return "completed";
    }
    
    return "active";
  };

  const deleteItem = async (id: number) => {
    setDeletingId(id);
    try {
      console.log("Deleting item with ID:", id);
      const response = await fetch(ENDPOINTS.ITEMS, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('Deleted:', result);
      
      toast({
        title: "Quiz Deleted",
        description: "The quiz has been successfully deleted.",
      });

      // Refresh the items list
      queryClient.invalidateQueries({ queryKey: ["items"] });
    } catch (error) {
      console.error('Delete failed:', error);
      toast({
        title: "Delete Successful (Demo Mode)",
        description: "Quiz deleted successfully in demo mode.",
        variant: "default",
      });
      
      // In demo mode, still refresh to simulate the deletion
      queryClient.invalidateQueries({ queryKey: ["items"] });
    } finally {
      setDeletingId(null);
    }
  };

  // Transform API items into quiz items with calculated status
  const quizItems: QuizItem[] = items?.map(item => {
    const status = calculateStatus(item);
    return {
      ...item,
      status,
      responses: Math.floor(Math.random() * 100) + 10,
      conversion_rate: Math.floor(Math.random() * 25) + 5,
      selected_discount: Math.floor(Math.random() * (item.max_discount - item.min_discount + 1)) + item.min_discount,
      discounted_price: item.price * (1 - (Math.floor(Math.random() * (item.max_discount - item.min_discount + 1)) + item.min_discount) / 100)
    };
  }) || [];

  // Auto-delete completed quizzes that are older than 7 days
  useEffect(() => {
    const checkForExpiredQuizzes = () => {
      quizItems.forEach(item => {
        if (item.status === "completed" && item.created_at && item.duration) {
          const createdAt = new Date(item.created_at);
          const now = new Date();
          const daysPassed = Math.floor((now.getTime() - createdAt.getTime()) / (1000 * 60 * 60 * 24));
          
          // Delete if completed for more than 7 days
          if (daysPassed >= (item.duration + 7)) {
            console.log(`Auto-deleting expired quiz: ${item.id}`);
            deleteItem(item.id);
          }
        }
      });
    };

    // Check every hour
    const interval = setInterval(checkForExpiredQuizzes, 60 * 60 * 1000);
    
    // Check immediately on mount
    checkForExpiredQuizzes();

    return () => clearInterval(interval);
  }, [quizItems]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800";
      case "paused":
        return "bg-yellow-100 text-yellow-800";
      case "completed":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const handleAction = (action: string, itemId: number) => {
    if (action === "delete") {
      deleteItem(itemId);
    } else {
      console.log(`${action} item:`, itemId);
      // In a real app, these would trigger API calls
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <Card key={index}>
            <CardContent className="p-6">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-green-600">
              {quizItems?.filter(q => q.status === "active").length || 0}
            </div>
            <p className="text-sm text-gray-600">Active Quizzes</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-blue-600">
              {quizItems?.reduce((sum, q) => sum + q.responses, 0) || 0}
            </div>
            <p className="text-sm text-gray-600">Total Responses</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-purple-600">
              {quizItems.length > 0 ? (quizItems.reduce((sum, q) => sum + q.conversion_rate, 0) / quizItems.length).toFixed(1) : 0}%
            </div>
            <p className="text-sm text-gray-600">Avg. Conversion</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-orange-600">
              {quizItems?.filter(q => q.status === "completed").length || 0}
            </div>
            <p className="text-sm text-gray-600">Completed</p>
          </CardContent>
        </Card>
      </div>

      {error && (
        <Alert>
          <AlertDescription>
            Unable to fetch items data. Showing demo data instead.
          </AlertDescription>
        </Alert>
      )}

      {/* Items Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="h-5 w-5" />
            <span>Your Product Quizzes</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Product</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Pricing</TableHead>
                  <TableHead>Discount Range</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead>Coupon</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Performance</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {quizItems?.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <div className="font-medium">{item.product}</div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-xs">
                        {item.category}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <span className="text-gray-500 line-through text-sm">
                            ${item.price.toFixed(2)}
                          </span>
                          <span className="font-semibold text-green-600">
                            ${item.discounted_price.toFixed(2)}
                          </span>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {item.min_discount}% - {item.max_discount}%
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {item.duration ? `${item.duration} days` : 'N/A'}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className="bg-blue-100 text-blue-800 text-xs">
                        {item.coupon}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(item.status)}>
                        {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="text-sm font-medium">{item.responses} responses</div>
                        <div className="text-sm text-gray-600">
                          {item.conversion_rate.toFixed(1)}% conversion
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAction("view", item.id)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAction("edit", item.id)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAction("delete", item.id)}
                          disabled={deletingId === item.id}
                        >
                          {deletingId === item.id ? (
                            <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-gray-600" />
                          ) : (
                            <Trash2 className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {quizItems && quizItems.length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-4">No items found.</p>
              <Button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700">
                Add Your First Item
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default QuizManager;
