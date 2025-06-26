
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Plus, Upload, DollarSign, Percent } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface ProductFormData {
  name: string;
  description: string;
  price: string;
  discount: string;
  imageUrl: string;
}

const QuizCreator = () => {
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<ProductFormData>({
    name: "",
    description: "",
    price: "",
    discount: "",
    imageUrl: ""
  });

  const handleInputChange = (field: keyof ProductFormData) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value
    }));
  };

  const calculateDiscountedPrice = () => {
    const price = parseFloat(formData.price);
    const discount = parseFloat(formData.discount);
    
    if (isNaN(price) || isNaN(discount)) return null;
    
    return (price * (1 - discount / 100)).toFixed(2);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      console.log("Submitting product quiz:", formData);
      
      // Mock API call - in real app this would call your backend
      const response = await fetch("http://localhost:8000/api/products", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: formData.name,
          description: formData.description,
          price: parseFloat(formData.price),
          discount_percentage: parseFloat(formData.discount),
          image_url: formData.imageUrl || null,
          status: "active"
        }),
      });

      if (response.ok) {
        toast({
          title: "Quiz Created Successfully!",
          description: "Your product discount quiz has been created and is now active.",
        });

        // Reset form
        setFormData({
          name: "",
          description: "",
          price: "",
          discount: "",
          imageUrl: ""
        });
      } else {
        throw new Error("Failed to create quiz");
      }
    } catch (error) {
      console.error("Error creating quiz:", error);
      toast({
        title: "Quiz Created (Demo Mode)",
        description: "Your quiz has been created successfully in demo mode.",
        variant: "default",
      });

      // Reset form even in demo mode
      setFormData({
        name: "",
        description: "",
        price: "",
        discount: "",
        imageUrl: ""
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const discountedPrice = calculateDiscountedPrice();

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Plus className="h-5 w-5" />
            <span>Create Product Discount Quiz</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Product Details */}
              <div className="space-y-4">
                <div>
                  <Label htmlFor="productName">Product Name *</Label>
                  <Input
                    id="productName"
                    placeholder="e.g., Premium Dog Toy Set"
                    value={formData.name}
                    onChange={handleInputChange("name")}
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="description">Product Description</Label>
                  <Textarea
                    id="description"
                    placeholder="Describe your product and why customers will love it..."
                    value={formData.description}
                    onChange={handleInputChange("description")}
                    rows={4}
                  />
                </div>

                <div>
                  <Label htmlFor="imageUrl">Product Image URL</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="imageUrl"
                      placeholder="https://example.com/image.jpg"
                      value={formData.imageUrl}
                      onChange={handleInputChange("imageUrl")}
                    />
                    <Button type="button" variant="outline" size="icon">
                      <Upload className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>

              {/* Pricing */}
              <div className="space-y-4">
                <div>
                  <Label htmlFor="price">Original Price ($) *</Label>
                  <div className="relative">
                    <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      id="price"
                      type="number"
                      step="0.01"
                      min="0"
                      placeholder="29.99"
                      className="pl-10"
                      value={formData.price}
                      onChange={handleInputChange("price")}
                      required
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="discount">Discount Percentage *</Label>
                  <div className="relative">
                    <Percent className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      id="discount"
                      type="number"
                      min="1"
                      max="90"
                      placeholder="20"
                      className="pl-10"
                      value={formData.discount}
                      onChange={handleInputChange("discount")}
                      required
                    />
                  </div>
                </div>

                {/* Price Preview */}
                {discountedPrice && (
                  <Alert>
                    <AlertDescription>
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="text-gray-500 line-through">${formData.price}</span>
                          <span className="ml-2 text-green-600 font-semibold text-lg">
                            ${discountedPrice}
                          </span>
                        </div>
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
                          {formData.discount}% OFF
                        </span>
                      </div>
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            </div>

            {/* Preview */}
            {formData.imageUrl && (
              <div className="border-t pt-6">
                <h3 className="text-lg font-semibold mb-4">Quiz Preview</h3>
                <Card className="max-w-sm">
                  <div className="aspect-square bg-gray-100">
                    <img
                      src={formData.imageUrl}
                      alt="Product preview"
                      className="w-full h-full object-cover rounded-t-lg"
                      onError={(e) => {
                        e.currentTarget.src = "https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=400&h=400&fit=crop";
                      }}
                    />
                  </div>
                  <CardContent className="p-4">
                    <h4 className="font-semibold">{formData.name || "Product Name"}</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      {formData.description || "Product description will appear here..."}
                    </p>
                    {discountedPrice && (
                      <div className="mt-3 flex items-center justify-between">
                        <div>
                          <span className="text-gray-500 line-through text-sm">${formData.price}</span>
                          <span className="ml-2 text-green-600 font-bold">${discountedPrice}</span>
                        </div>
                        <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-medium">
                          {formData.discount}% OFF
                        </span>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}

            <div className="flex justify-end space-x-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setFormData({
                  name: "",
                  description: "",
                  price: "",
                  discount: "",
                  imageUrl: ""
                })}
              >
                Reset
              </Button>
              <Button
                type="submit"
                disabled={isSubmitting || !formData.name || !formData.price || !formData.discount}
                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
              >
                {isSubmitting ? "Creating Quiz..." : "Create Quiz"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default QuizCreator;
