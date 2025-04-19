import { AppSidebar } from "@/components/app-sidebar";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { JSX } from "react";
import { ModeToggle } from "@/components/mode-toggle.tsx";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar.tsx";
import { LayoutProps } from "@/types/Types.ts";
import { ScrollArea } from "@/components/ui/scroll-area";
import { getInitials } from "@/components/nav-user";
import { useUser } from "@/auth";
import { useLocation } from "react-router-dom";

// Define route title mapping
const routeTitles: Record<string, string> = {
  "/": "Dashboard",
  "/chat": "Chat with Data",
  "/trend": "Trend Analysis",
  "/view-report": "View Report",
  "/settings": "Settings",
  "/profile": "Profile",
  // Add more routes as needed
};

export default function Layout({ children }: LayoutProps): JSX.Element {
  const user = useUser();
  const userInitials = getInitials(user?.name || user?.username || "");
  const location = useLocation();
  
  // Get current path and generate breadcrumb items
  const currentPath = location.pathname;
  
  // Generate breadcrumb items based on the path
  const getBreadcrumbItems = () => {
    // If we're at home page, just show "Home"
    if (currentPath === "/") {
      return (
        <>
          <BreadcrumbItem>
            <BreadcrumbPage>Dashboard</BreadcrumbPage>
          </BreadcrumbItem>
        </>
      );
    }
    
    // Otherwise show Home > Current Page
    return (
      <>
        <BreadcrumbItem className="hidden md:block">
          <BreadcrumbLink href="/">Home</BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator className="hidden md:block" />
        <BreadcrumbItem>
          <BreadcrumbPage>
            {routeTitles[currentPath] || 
              currentPath.split("/").pop()?.replace(/-/g, " ")
                .split(" ")
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(" ") || 
              "Page"}
          </BreadcrumbPage>
        </BreadcrumbItem>
      </>
    );
  };
  
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center justify-between pr-4 gap-2  transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12 border-0 border-b-1">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger />
            <Avatar>
              <AvatarImage src={user?.avatar} alt={user?.name} />
              <AvatarFallback>{userInitials}</AvatarFallback>
            </Avatar>
            <Separator orientation="vertical" className="mr-2 h-4" />
            <Breadcrumb>
              <BreadcrumbList>
                {getBreadcrumbItems()}
              </BreadcrumbList>
            </Breadcrumb>
          </div>
          <ModeToggle />
        </header>

        {/* Using ScrollArea for inner scrolling */}
        <ScrollArea className="h-[calc(100vh-4rem)]">
          <div className="flex flex-1 flex-col gap-4 p-4">
            {children}
          </div>
        </ScrollArea>
      </SidebarInset>
    </SidebarProvider>
  );
}
