
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Eye, Edit, Trash2, BarChart3 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

interface Quiz {
  id: string;
  product_name: string;
  original_price: number;
  discount_percentage: number;
  discounted_price: number;
  status: "active" | "paused" | "completed";
  responses: number;
  conversion_rate: number;
  created_at: string;
  image_url?: string;
}

const QuizManager = () => {
  const { data: quizzes, isLoading, error } = useQuery({
    queryKey: ["quizzes"],
    queryFn: async (): Promise<Quiz[]> => {
      console.log("Fetching quiz data...");
      
      // Mock API call - in real app this would call your backend
      const response = await fetch("http://localhost:8000/api/quizzes");
      
      if (!response.ok) {
        // Return mock data if API fails
        return [
          {
            id: "1",
            product_name: "Premium Dog Toy Set",
            original_price: 29.99,
            discount_percentage: 20,
            discounted_price: 23.99,
            status: "active",
            responses: 45,
            conversion_rate: 12.2,
            created_at: "2024-01-15T10:30:00Z",
            image_url: "https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=100&h=100&fit=crop"
          },
          {
            id: "2",
            product_name: "Interactive Puzzle Feeder",
            original_price: 39.99,
            discount_percentage: 25,
            discounted_price: 29.99,
            status: "active",
            responses: 28,
            conversion_rate: 18.5,
            created_at: "2024-01-14T14:22:00Z",
            image_url: "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=100&h=100&fit=crop"
          },
          {
            id: "3",
            product_name: "Cozy Cat Bed",
            original_price: 49.99,
            discount_percentage: 15,
            discounted_price: 42.49,
            status: "paused",
            responses: 67,
            conversion_rate: 8.9,
            created_at: "2024-01-13T09:15:00Z",
            image_url: "https://images.unsplash.com/photo-1574144611937-0df059b5ef3e?w=100&h=100&fit=crop"
          },
          {
            id: "4",
            product_name: "Natural Chicken Treats",
            original_price: 19.99,
            discount_percentage: 30,
            discounted_price: 13.99,
            status: "completed",
            responses: 156,
            conversion_rate: 24.3,
            created_at: "2024-01-12T16:45:00Z",
            image_url: "https://images.unsplash.com/photo-1605568427561-40dd23c2acea?w=100&h=100&fit=crop"
          }
        ];
      }
      
      return response.json();
    },
  });

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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const handleAction = (action: string, quizId: string) => {
    console.log(`${action} quiz:`, quizId);
    // In a real app, these would trigger API calls
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
              {quizzes?.filter(q => q.status === "active").length || 0}
            </div>
            <p className="text-sm text-gray-600">Active Quizzes</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-blue-600">
              {quizzes?.reduce((sum, q) => sum + q.responses, 0) || 0}
            </div>
            <p className="text-sm text-gray-600">Total Responses</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-purple-600">
              {quizzes ? (quizzes.reduce((sum, q) => sum + q.conversion_rate, 0) / quizzes.length).toFixed(1) : 0}%
            </div>
            <p className="text-sm text-gray-600">Avg. Conversion</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-2xl font-bold text-orange-600">
              {quizzes?.filter(q => q.status === "completed").length || 0}
            </div>
            <p className="text-sm text-gray-600">Completed</p>
          </CardContent>
        </Card>
      </div>

      {error && (
        <Alert>
          <AlertDescription>
            Unable to fetch quiz data. Showing demo data instead.
          </AlertDescription>
        </Alert>
      )}

      {/* Quizzes Table */}
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
                  <TableHead>Pricing</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Performance</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {quizzes?.map((quiz) => (
                  <TableRow key={quiz.id}>
                    <TableCell>
                      <div className="flex items-center space-x-3">
                        {quiz.image_url && (
                          <img
                            src={quiz.image_url}
                            alt={quiz.product_name}
                            className="w-10 h-10 rounded object-cover"
                          />
                        )}
                        <div>
                          <div className="font-medium">{quiz.product_name}</div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <span className="text-gray-500 line-through text-sm">
                            ${quiz.original_price}
                          </span>
                          <span className="font-semibold text-green-600">
                            ${quiz.discounted_price}
                          </span>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {quiz.discount_percentage}% OFF
                        </Badge>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(quiz.status)}>
                        {quiz.status.charAt(0).toUpperCase() + quiz.status.slice(1)}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="text-sm font-medium">{quiz.responses} responses</div>
                        <div className="text-sm text-gray-600">
                          {quiz.conversion_rate}% conversion
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-gray-600">
                      {formatDate(quiz.created_at)}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAction("view", quiz.id)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAction("edit", quiz.id)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAction("delete", quiz.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {quizzes && quizzes.length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-4">No quizzes created yet.</p>
              <Button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700">
                Create Your First Quiz
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default QuizManager;
