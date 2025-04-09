import * as z from "zod";

export const formSchema = z.object({
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
    .string()
    .url({
      message: "Please enter a valid URL.",
    })
    .optional()
    .or(z.literal("")),
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

export interface Register {
    username: string;
    email: string;
    phone: string;
    password: string;
}


export interface Login {
    email: string;
    password: string;
}