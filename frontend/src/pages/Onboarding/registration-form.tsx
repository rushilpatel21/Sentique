"use client"

import { useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Button } from "@/components/ui/button.tsx"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form.tsx"
import { Input } from "@/components/ui/input.tsx"
import { toast } from "sonner"
import { useOnboarding } from "@/lib/onboarding-context.tsx"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card.tsx"
import { Loader2 } from "lucide-react"

// Form validation schema
const formSchema = z.object({
  firstName: z.string().min(2, {
    message: "First name must be at least 2 characters.",
  }),
  lastName: z.string().min(2, {
    message: "Last name must be at least 2 characters.",
  }),
  designation: z.string().min(2, {
    message: "Designation must be at least 2 characters.",
  }),
  password: z.string()
    .min(8, "Password must be at least 8 characters")
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
      "Password must contain at least one uppercase letter, one lowercase letter, one number and one special character"),
  companyName: z.string().min(2, {
    message: "Company name must be at least 2 characters.",
  }),
  email: z.string().email({
    message: "Please enter a valid email address.",
  }),
  mobileNumber: z.string().regex(/^\+?[0-9]{10,15}$/, {
    message: "Please enter a valid mobile number.",
  }),
  websiteUrl: z
    .string(),
  googlePlayAppId: z
    .string()
    .regex(/^([a-z][a-z0-9_]*\.)+[a-z][a-z0-9_]*$/, {
      message: "Please enter a valid Google Play app ID (e.g., com.example.app).",
    })
    .optional()
    .or(z.literal("")),
  appleAppStoreId: z.string().optional().or(z.literal("")),
  appleAppStoreName: z.string().optional().or(z.literal("")),
})

export function OnboardForm() {
  const { formData, setFormData, submitForm, status, errorMessage } = useOnboarding()
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Initialize form with existing data from store
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: formData,
  })

  // Handle form submission
  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      setIsSubmitting(true)
      // Update form data in store
      setFormData(values)
      // Submit form data
      console.log(values)
      await submitForm(values)

      toast( "Registration submitted",{
        description: "Your registration is being processed."
      })
    } catch (error) {
      toast("Submission failed",{
        description: "There was an error submitting your registration. Please try again.",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="container mx-auto py-10">
      <Card>
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold">Create your account</CardTitle>
          <CardDescription>Enter your information to get started with our platform</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <FormField
                  control={form.control}
                  name="firstName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>First name</FormLabel>
                      <FormControl>
                        <Input placeholder="John" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="lastName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Last name</FormLabel>
                      <FormControl>
                        <Input placeholder="Doe" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <FormField
                  control={form.control}
                  name="designation"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Designation</FormLabel>
                      <FormControl>
                        <Input placeholder="Product Manager" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="companyName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Company name</FormLabel>
                      <FormControl>
                        <Input placeholder="Acme Inc." {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input type="email" placeholder="john.doe@example.com" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="mobileNumber"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Mobile number</FormLabel>
                      <FormControl>
                        <Input placeholder="+1234567890" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <FormField
                control={form.control}
                name="websiteUrl"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Website URL</FormLabel>
                    <FormControl>
                      <Input  placeholder="https://example.com" {...field} />
                    </FormControl>
                    <FormDescription>Your company website (optional)</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
                <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Password</FormLabel>
                    <FormControl>
                      <Input type={"password"} {...field} />
                    </FormControl>
                    <FormDescription>8 character minimun</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              </div>


              <div className="space-y-4">
                <h3 className="text-lg font-medium">App Information</h3>
                <div className="grid grid-cols-1 gap-4">
                  <FormField
                    control={form.control}
                    name="googlePlayAppId"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Google Play App ID</FormLabel>
                        <FormControl>
                          <Input placeholder="com.example.app" {...field} />
                        </FormControl>
                        <FormDescription>The package name of your Android app (optional)</FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <FormField
                    control={form.control}
                    name="appleAppStoreId"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Apple App Store ID</FormLabel>
                        <FormControl>
                          <Input placeholder="123456789" {...field} />
                        </FormControl>
                        <FormDescription>Your iOS app ID (optional)</FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="appleAppStoreName"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Apple App Store Name</FormLabel>
                        <FormControl>
                          <Input placeholder="MyApp" {...field} />
                        </FormControl>
                        <FormDescription>Your iOS app name (optional)</FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </div>

              {errorMessage && (
                <div className="rounded-md bg-destructive/15 p-3 text-sm text-destructive">{errorMessage}</div>
              )}

              <Button type="submit" className="w-full" disabled={isSubmitting || status === "submitting"}>
                {(isSubmitting || status === "submitting") && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Register
              </Button>
            </form>
          </Form>
        </CardContent>
        <CardFooter className="flex justify-center border-t px-6 py-4">
          <p className="text-xs text-muted-foreground">
            By clicking Register, you agree to our{" "}
            <a href="#" className="underline underline-offset-4 hover:text-primary">
              Terms of Service
            </a>{" "}
            and{" "}
            <a href="#" className="underline underline-offset-4 hover:text-primary">
              Privacy Policy
            </a>
            .
          </p>
        </CardFooter>
      </Card>
    </div>
  )
}

