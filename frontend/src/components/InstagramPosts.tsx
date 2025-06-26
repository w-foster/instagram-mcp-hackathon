
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Heart, MessageCircle, Search } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

interface InstagramPost {
  id: string;
  caption: string;
  image_url: string;
  like_count: number;
  comment_count: number;
  created_at: string;
}

const InstagramPosts = () => {
  const [username, setUsername] = useState("petstore_demo");
  const [searchUsername, setSearchUsername] = useState("petstore_demo");

  const { data: posts, isLoading, error, refetch } = useQuery({
    queryKey: ["instagram-posts", searchUsername],
    queryFn: async (): Promise<InstagramPost[]> => {
      console.log(`Fetching Instagram posts for: ${searchUsername}`);
      
      // Mock API call - in real app this would call your backend
      const response = await fetch(`http://localhost:8000/api/user_posts?username=${searchUsername}`);
      
      if (!response.ok) {
        // Return mock data if API fails
        return [
          {
            id: "1",
            caption: "🐕 New puppy toys just arrived! Perfect for training and playtime. Which one does your furry friend need? #puppylife #toys",
            image_url: "https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=400&h=400&fit=crop",
            like_count: 342,
            comment_count: 28,
            created_at: "2024-01-15T10:30:00Z"
          },
          {
            id: "2", 
            caption: "🎾 Interactive puzzle feeders - keep your dogs mentally stimulated while they eat! Available in 3 sizes. #doghealth #puzzlefeeder",
            image_url: "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=400&h=400&fit=crop",
            like_count: 287,
            comment_count: 15,
            created_at: "2024-01-14T14:22:00Z"
          },
          {
            id: "3",
            caption: "😻 Cat lovers, this cozy bed is flying off our shelves! Your feline friends will thank you. Limited stock! #catbed #cozy",
            image_url: "https://images.unsplash.com/photo-1574144611937-0df059b5ef3e?w=400&h=400&fit=crop",
            like_count: 198,
            comment_count: 12,
            created_at: "2024-01-13T09:15:00Z"
          },
          {
            id: "4",
            caption: "🦴 Premium natural treats made with real chicken. No artificial preservatives - just pure goodness for your pup! #healthytreats",
            image_url: "https://images.unsplash.com/photo-1605568427561-40dd23c2acea?w=400&h=400&fit=crop",
            like_count: 421,
            comment_count: 33,
            created_at: "2024-01-12T16:45:00Z"
          }
        ];
      }
      
      return response.json();
    },
    enabled: !!searchUsername,
  });

  const handleSearch = () => {
    setSearchUsername(username);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Search className="h-5 w-5" />
            <span>Instagram Account</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-4">
            <Input
              placeholder="Enter Instagram username..."
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="flex-1"
            />
            <Button onClick={handleSearch} disabled={isLoading}>
              {isLoading ? "Loading..." : "Fetch Posts"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {error && (
        <Alert>
          <AlertDescription>
            Unable to fetch Instagram posts. Showing demo data instead.
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          // Loading skeletons
          Array.from({ length: 6 }).map((_, index) => (
            <Card key={index} className="overflow-hidden">
              <Skeleton className="h-64 w-full" />
              <CardContent className="p-4">
                <Skeleton className="h-4 w-full mb-2" />
                <Skeleton className="h-4 w-3/4 mb-4" />
                <div className="flex space-x-4">
                  <Skeleton className="h-4 w-16" />
                  <Skeleton className="h-4 w-16" />
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          // Posts grid
          posts?.map((post) => (
            <Card key={post.id} className="overflow-hidden hover:shadow-lg transition-shadow duration-200">
              <div className="aspect-square bg-gray-100">
                <img
                  src={post.image_url}
                  alt="Instagram post"
                  className="w-full h-full object-cover"
                />
              </div>
              <CardContent className="p-4">
                <p className="text-sm text-gray-700 mb-3 line-clamp-3">
                  {post.caption}
                </p>
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-1">
                      <Heart className="h-4 w-4" />
                      <span>{post.like_count}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <MessageCircle className="h-4 w-4" />
                      <span>{post.comment_count}</span>
                    </div>
                  </div>
                  <span>{formatDate(post.created_at)}</span>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {posts && posts.length === 0 && !isLoading && (
        <Card>
          <CardContent className="p-8 text-center">
            <p className="text-gray-500">No posts found for this username.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default InstagramPosts;
