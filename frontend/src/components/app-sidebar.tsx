import * as React from "react"
import {
  AudioWaveform,
  BotMessageSquare,
  Command, Database, FileText,
  GalleryVerticalEnd, Home,
  TrendingUp,
} from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavUser } from "@/components/nav-user"
import { TeamSwitcher } from "@/components/team-switcher"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar"

import { useUser } from "@/auth/hooks"

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const user = useUser(); // Fetch user details from the backend

  // Handle loading state
  if (!user) {
    return <p>Loading...</p>;
  }

  const data = {
    user: {
      name: user.username || "Unknown User",
      email: user.email || "No email available",
      avatar: user.avatar || "/avatars/default.jpg",
    },
    teams: [
      {
        name: "SentimentIQ",
        logo: GalleryVerticalEnd,
        plan: "Enterprise",
      },
      {
        name: "Acme Corp.",
        logo: AudioWaveform,
        plan: "Startup",
      },
      {
        name: "Evil Corp.",
        logo: Command,
        plan: "Free",
      },
    ],
    navMain: [
      {
        title: "Home",
        url: "/",
        icon: Home,
        isActive: true,
      },
      {
        title: "View Report",
        url: "/view-report",
        icon: FileText,
      },
      {
        title: "Trend Analysis",
        url: "/trend",
        icon: TrendingUp,
      },
      {
        title: "Chat with your Data",
        url: "/chat",
        icon: BotMessageSquare,
      },
    ]
  
}

  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <TeamSwitcher teams={data.teams} />
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user}  />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
