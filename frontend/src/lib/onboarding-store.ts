import { create } from "zustand"
import { persist } from "zustand/middleware"

export type OnboardingStatus = "idle" | "submitting" | "processing" | "completed" | "error"

export interface UserFormData {
  firstName: string
  lastName: string
  designation: string
  companyName: string
  email: string
  password: string
  mobileNumber: string
  websiteUrl: string
  googlePlayAppId: string
  appleAppStoreId: string
  appleAppStoreName: string
}

interface OnboardingState {
  currentStep: number
  status: OnboardingStatus
  formData: UserFormData
  errorMessage: string | null
  setStep: (step: number) => void
  setStatus: (status: OnboardingStatus) => void
  setFormData: (data: Partial<UserFormData>) => void
  setErrorMessage: (message: string | null) => void
  resetOnboarding: () => void
}

const initialFormData: UserFormData = {
  firstName: "",
  lastName: "",
  designation: "",
  companyName: "",
  email: "",
  password:"",
  mobileNumber: "",
  websiteUrl: "",
  googlePlayAppId: "",
  appleAppStoreId: "",
  appleAppStoreName: "",
}

export const useOnboardingStore = create<OnboardingState>()(
  persist(
    (set) => ({
      currentStep: 0,
      status: "idle",
      formData: initialFormData,
      errorMessage: null,
      setStep: (step) => set({ currentStep: step }),
      setStatus: (status) => set({ status }),
      setFormData: (data) =>
        set((state) => ({
          formData: { ...state.formData, ...data },
        })),
      setErrorMessage: (message) => set({ errorMessage: message }),
      resetOnboarding: () =>
        set({
          currentStep: 0,
          status: "idle",
          formData: initialFormData,
          errorMessage: null,
        }),
    }),
    {
      name: "onboarding-storage",
    },
  ),
)

