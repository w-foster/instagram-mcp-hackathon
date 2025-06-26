
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useNavigate } from "react-router-dom";
import { LogOut, Plus, Instagram, BarChart3 } from "lucide-react";
import InstagramPosts from "@/components/InstagramPosts";
import QuizCreator from "@/components/QuizCreator";
import QuizManager from "@/components/QuizManager";

const Dashboard = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("posts");

  const handleLogout = () => {
    // Mock logout - in real app this would clear auth state
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg"></div>
            <h1 className="text-xl font-bold text-gray-900">QuizWizard Dashboard</h1>
          </div>
          <Button variant="ghost" onClick={handleLogout} className="flex items-center space-x-2">
            <LogOut className="h-4 w-4" />
            <span>Logout</span>
          </Button>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r border-gray-200 min-h-screen p-6">
          <nav className="space-y-2">
            <Button
              variant={activeTab === "posts" ? "default" : "ghost"}
              className="w-full justify-start"
              onClick={() => setActiveTab("posts")}
            >
              <Instagram className="h-4 w-4 mr-3" />
              Instagram Posts
            </Button>
            <Button
              variant={activeTab === "create" ? "default" : "ghost"}
              className="w-full justify-start"
              onClick={() => setActiveTab("create")}
            >
              <Plus className="h-4 w-4 mr-3" />
              Create Quiz
            </Button>
            <Button
              variant={activeTab === "manage" ? "default" : "ghost"}
              className="w-full justify-start"
              onClick={() => setActiveTab("manage")}
            >
              <BarChart3 className="h-4 w-4 mr-3" />
              Manage Quizzes
            </Button>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          <div className="max-w-6xl mx-auto">
            {/* Welcome Card */}
            <Card className="mb-8 border-0 shadow-sm bg-gradient-to-r from-purple-50 to-blue-50">
              <CardContent className="p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Welcome back! 👋
                </h2>
                <p className="text-gray-600">
                  Ready to create some engaging discount quizzes? Start by checking your latest Instagram posts.
                </p>
              </CardContent>
            </Card>

            {/* Tab Content */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="mb-6">
                <TabsTrigger value="posts">Instagram Posts</TabsTrigger>
                <TabsTrigger value="create">Create Quiz</TabsTrigger>
                <TabsTrigger value="manage">Manage Quizzes</TabsTrigger>
              </TabsList>

              <TabsContent value="posts">
                <InstagramPosts />
              </TabsContent>

              <TabsContent value="create">
                <QuizCreator />
              </TabsContent>

              <TabsContent value="manage">
                <QuizManager />
              </TabsContent>
            </Tabs>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
