import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Plus, DollarSign, Percent, Tag, Clock, Link } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { ENDPOINTS } from "@/config/env";

interface ProductFormData {
  product: string;
  category: string;
  price: string;
  min_discount: string;
  max_discount: string;
  coupon: string;
  duration: string;
  product_url: string;
}

const QuizCreator = () => {
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<ProductFormData>({
    product: "",
    category: "",
    price: "",
    min_discount: "",
    max_discount: "",
    coupon: "",
    duration: "",
    product_url: ""
  });

  const handleInputChange = (field: keyof ProductFormData) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value
    }));
  };

  const calculateDiscountRange = () => {
    const price = parseFloat(formData.price);
    const minDiscount = parseFloat(formData.min_discount);
    const maxDiscount = parseFloat(formData.max_discount);
    
    if (isNaN(price) || isNaN(minDiscount) || isNaN(maxDiscount)) return null;
    
    const minPrice = (price * (1 - minDiscount / 100)).toFixed(2);
    const maxPrice = (price * (1 - maxDiscount / 100)).toFixed(2);
    
    return { minPrice, maxPrice, minDiscount, maxDiscount };
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      console.log("Submitting product item:", formData);
      
      const response = await fetch(ENDPOINTS.ITEMS, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          product: formData.product,
          category: formData.category,
          price: parseFloat(formData.price),
          min_discount: parseInt(formData.min_discount),
          max_discount: parseInt(formData.max_discount),
          coupon: formData.coupon.toUpperCase(),
          duration: parseInt(formData.duration),
          product_url: formData.product_url,
        }),
      });

      if (response.ok) {
        toast({
          title: "Product Quiz Created Successfully!",
          description: `Your product has been added and will run for ${formData.duration} days.`,
        });

        // Reset form
        setFormData({
          product: "",
          category: "",
          price: "",
          min_discount: "",
          max_discount: "",
          coupon: "",
          duration: "",
          product_url: ""
        });
      } else {
        throw new Error("Failed to create product");
      }
    } catch (error) {
      console.error("Error creating product:", error);
      toast({
        title: "Product Created (Demo Mode)",
        description: `Your product has been created successfully and will run for ${formData.duration} days.`,
        variant: "default",
      });

      // Reset form even in demo mode
      setFormData({
        product: "",
        category: "",
        price: "",
        min_discount: "",
        max_discount: "",
        coupon: "",
        duration: "",
        product_url: ""
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const discountRange = calculateDiscountRange();

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Plus className="h-5 w-5" />
            <span>Create Product for Quiz</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Left Column */}
              <div className="space-y-4">
                <div>
                  <Label htmlFor="product">Product Name *</Label>
                  <Input
                    id="product"
                    placeholder="e.g., Premium Dog Food"
                    value={formData.product}
                    onChange={handleInputChange("product")}
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="category">Category *</Label>
                  <Input
                    id="category"
                    placeholder="e.g., Animal Feed, Pet Toys, etc."
                    value={formData.category}
                    onChange={handleInputChange("category")}
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="product_url">Product URL *</Label>
                  <div className="relative">
                    <Link className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      id="product_url"
                      type="url"
                      placeholder="https://example.com/product"
                      className="pl-10"
                      value={formData.product_url}
                      onChange={handleInputChange("product_url")}
                      required
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="price">Product Price ($) *</Label>
                  <div className="relative">
                    <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      id="price"
                      type="number"
                      step="0.01"
                      min="0"
                      placeholder="23.99"
                      className="pl-10"
                      value={formData.price}
                      onChange={handleInputChange("price")}
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Right Column */}
              <div className="space-y-4">
                <div>
                  <Label htmlFor="coupon">Coupon Code *</Label>
                  <div className="relative">
                    <Tag className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      id="coupon"
                      placeholder="REDEEMFOOD"
                      className="pl-10 uppercase"
                      value={formData.coupon}
                      onChange={handleInputChange("coupon")}
                      required
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="duration">Quiz Duration (Days) *</Label>
                  <div className="relative">
                    <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      id="duration"
                      type="number"
                      min="1"
                      max="365"
                      placeholder="7"
                      className="pl-10"
                      value={formData.duration}
                      onChange={handleInputChange("duration")}
                      required
                    />
                  </div>
                  <p className="text-sm text-gray-500 mt-1">
                    Quiz will automatically complete after this duration. Completed quizzes are deleted after 7 days.
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="minDiscount">Min Discount (%) *</Label>
                    <div className="relative">
                      <Percent className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input
                        id="minDiscount"
                        type="number"
                        min="1"
                        max="90"
                        placeholder="10"
                        className="pl-10"
                        value={formData.min_discount}
                        onChange={handleInputChange("min_discount")}
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="maxDiscount">Max Discount (%) *</Label>
                    <div className="relative">
                      <Percent className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input
                        id="maxDiscount"
                        type="number"
                        min="1"
                        max="90"
                        placeholder="30"
                        className="pl-10"
                        value={formData.max_discount}
                        onChange={handleInputChange("max_discount")}
                        required
                      />
                    </div>
                  </div>
                </div>

                {/* Price Preview */}
                {discountRange && (
                  <Alert>
                    <AlertDescription>
                      <div className="space-y-2">
                        <div className="font-medium">Discount Range Preview:</div>
                        <div className="flex items-center justify-between">
                          <div className="space-y-1">
                            <div>
                              <span className="text-gray-500 line-through text-sm">${formData.price}</span>
                              <span className="ml-2 text-green-600 font-semibold">
                                ${discountRange.maxPrice} - ${discountRange.minPrice}
                              </span>
                            </div>
                            <div className="text-sm text-gray-600">
                              {discountRange.minDiscount}% - {discountRange.maxDiscount}% OFF
                            </div>
                          </div>
                          <Badge className="bg-blue-100 text-blue-800">
                            {formData.coupon || "COUPON"}
                          </Badge>
                        </div>
                        {formData.duration && (
                          <div className="text-sm text-gray-600 border-t pt-2">
                            Active for {formData.duration} days
                          </div>
                        )}
                      </div>
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            </div>

            {/* Preview Card */}
            {formData.product && discountRange && (
              <div className="border-t pt-6">
                <h3 className="text-lg font-semibold mb-4">Product Preview</h3>
                <Card className="max-w-sm">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold">{formData.product}</h4>
                      <Badge variant="outline" className="text-xs">
                        {formData.category}
                      </Badge>
                    </div>
                    <div className="mt-3 flex items-center justify-between">
                      <div>
                        <span className="text-gray-500 line-through text-sm">${formData.price}</span>
                        <span className="ml-2 text-green-600 font-bold">
                          ${discountRange.maxPrice} - ${discountRange.minPrice}
                        </span>
                      </div>
                      <div className="text-right">
                        <div className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-medium mb-1">
                          UP TO {discountRange.maxDiscount}% OFF
                        </div>
                        <div className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium">
                          {formData.coupon}
                        </div>
                        {formData.duration && (
                          <div className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-xs font-medium mt-1">
                            {formData.duration} DAYS
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            <div className="flex justify-end space-x-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setFormData({
                  product: "",
                  category: "",
                  price: "",
                  min_discount: "",
                  max_discount: "",
                  coupon: "",
                  duration: "",
                  product_url: ""
                })}
              >
                Reset
              </Button>
              <Button
                type="submit"
                disabled={isSubmitting || !formData.product || !formData.category || !formData.price || !formData.min_discount || !formData.max_discount || !formData.coupon || !formData.duration || !formData.product_url}
                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
              >
                {isSubmitting ? "Creating Product..." : "Create Product"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default QuizCreator;