import {AuthContextProvider} from "@/auth";
import Router from "@/routes/Routes.tsx";
import {ThemeProvider} from "@/components/theme-provider.tsx";
import { Toaster } from "@/components/ui/sonner"
import {OnboardingProvider} from "@/lib/onboarding-context.tsx";

function App() {

  return (
      <AuthContextProvider>
          <ThemeProvider>
              <OnboardingProvider>
            <Router/><Toaster />
              </OnboardingProvider>
          </ThemeProvider>
      </AuthContextProvider>
  )
}

export default App
