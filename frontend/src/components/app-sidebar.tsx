import * as React from "react"
import {
  AudioWaveform,
  BookOpen,
  Bot,
  Command,
  Frame,
  GalleryVerticalEnd,
  Map,
  PieChart,
  Settings2,
  SquareTerminal,
} from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavProjects } from "@/components/nav-projects"
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
        url: "#",
        icon: SquareTerminal,
        isActive: true,
      },
      {
        title: "View Report",
        url: "#",
        icon: Bot,
      },
      {
        title: "Trend Analysis",
        url: "#",
        icon: BookOpen,
      },
      {
        title: "Chat with your Data",
        url: "/chat",
        icon: Settings2,
      },
      {
        title: "View Data Source",
        url: "#",
        icon: Settings2,
      },
    ],
    projects: [
      {
        name: "Design Engineering",
        url: "#",
        icon: Frame,
      },
      {
        name: "Sales & Marketing",
        url: "#",
        icon: PieChart,
      },
      {
        name: "Travel",
        url: "#",
        icon: Map,
      },
    ],
  }

  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <TeamSwitcher teams={data.teams} />
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
        <NavProjects projects={data.projects} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
