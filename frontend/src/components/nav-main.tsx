"use client"

import {  type LucideIcon } from "lucide-react"
import { useNavigate } from "react-router-dom" // ✅ Import navigation hook


import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

export function NavMain({
  items,
}: {
  items: {
    title: string
    url?: string
    onClick?: () => void // ✅ Support navigation clicks
    icon?: LucideIcon
    isActive?: boolean
    items?: {
      title: string
      url: string
    }[]
  }[]
}) {
  const navigate = useNavigate(); // ✅ Initialize navigation function

  return (
    <SidebarGroup>
      <SidebarGroupLabel>Platform</SidebarGroupLabel>
      <SidebarMenu>
        {items.map((item) => (
            <SidebarMenuItem>
                <SidebarMenuButton
                  tooltip={item.title}
                  className={"cursor-pointer"}
                  onClick={() => {
                    if (item.onClick) {
                      item.onClick(); // ✅ Handle click event
                    } else if (item.url) {
                      navigate(item.url); // ✅ Navigate if URL is provided
                    }
                  }}
                >
                  {item.icon && <item.icon />}
                  <span>{item.title}</span>
                </SidebarMenuButton>
            </SidebarMenuItem>
        ))}
      </SidebarMenu>
    </SidebarGroup>
  )
}
