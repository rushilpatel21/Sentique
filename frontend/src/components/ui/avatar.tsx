"use client";

import * as React from "react";
import * as AvatarPrimitive from "@radix-ui/react-avatar";

import { cn } from "@/lib/utils";

function Avatar({
  className,
  ...props
}: React.ComponentProps<typeof AvatarPrimitive.Root>) {
  return (
    <AvatarPrimitive.Root
      data-slot="avatar"
      className={cn(
        "relative flex size-8 shrink-0 overflow-hidden rounded-full",
        className
      )}
      {...props}
    />
  );
}

function AvatarImage({
  className,
  ...props
}: React.ComponentProps<typeof AvatarPrimitive.Image>) {
  return (
    <AvatarPrimitive.Image
      data-slot="avatar-image"
      className={cn("aspect-square size-full", className)}
      {...props}
    />
  );
}

function AvatarFallback({
  className,
  children,
  ...props
}: React.ComponentProps<typeof AvatarPrimitive.Fallback>) {
  return (
    <AvatarPrimitive.Fallback
      data-slot="avatar-fallback"
      className={cn(
        "bg-muted flex size-full items-center justify-center rounded-full text-lg font-medium text-white",
        className
      )}
      {...props}
    >
      {children}
    </AvatarPrimitive.Fallback>
  );
}

function ProfileIcon({ name, imageUrl }: { name: string; imageUrl?: string }) {
  const initial = name ? name.charAt(0).toUpperCase() : "?"; // Get first letter, fallback to "?"
  
  return (
    <Avatar>
      {/* Profile Image (if available) */}
      <AvatarImage src={imageUrl} alt={name} />
      {/* Fallback: Display First Letter of Name */}
      <AvatarFallback>{initial}</AvatarFallback>
    </Avatar>
  );
}

export { Avatar, AvatarImage, AvatarFallback, ProfileIcon };
