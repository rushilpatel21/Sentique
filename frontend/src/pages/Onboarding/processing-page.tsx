"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card.tsx"
import { Button } from "@/components/ui/button.tsx"
import { Loader2, CheckCircle, AlertCircle, RefreshCw } from "lucide-react"
import { useUser } from "@/auth"

export function ProcessingPage() {
  const { is_onboarded = false, step_status = {} } = useUser() || {};
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState("processing") // "processing", "completed", "error"
  const [errorMessage, setErrorMessage] = useState("")

  // Determine status based on user data
  useEffect(() => {
    if (is_onboarded) {
      setStatus("completed")
    } else {
      // Check if any steps have errors or are incomplete
      const allStepsCompleted = Object.values(step_status).every(
        step => step === "completed" || typeof step === "object"
      )

      // Check substeps if they exist
      const allSubstepsCompleted = step_status.step1_substeps ?
        Object.values(step_status.step1_substeps).every(substep => substep === "completed") :
        true

      if (allStepsCompleted && allSubstepsCompleted) {
        setStatus("completed")
      } else if (Object.values(step_status).some(step => step === "error") ||
                (step_status.step1_substeps && Object.values(step_status.step1_substeps).some(substep => substep === "error"))) {
        setStatus("error")
        setErrorMessage("One or more steps failed to complete. Please try again.")
      } else {
        setStatus("processing")
      }
    }
  }, [is_onboarded, step_status])


  const handleManualCheck = () => {
    // Simply refresh the page to get the latest user data
    window.location.reload()
  }

  return (
    <div className="container max-w-md mx-auto py-10">
      <Card>
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">
            {status === "completed"
              ? "Setup Complete!"
              : status === "error"
                ? "Processing Error"
                : "Setting Up Your Account"}
          </CardTitle>
          <CardDescription className="text-center">
            {status === "completed"
              ? "Your account has been successfully set up."
              : status === "error"
                ? "There was an error processing your registration."
                : "We are processing your registration. This may take a few minutes."}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-center mb-4">
            {status === "processing" && (
              <div className="rounded-full bg-primary/10 p-3">
                <Loader2 className="h-12 w-12 text-primary animate-spin" />
              </div>
            )}
            {status === "completed" && (
              <div className="rounded-full bg-green-100 p-3">
                <CheckCircle className="h-12 w-12 text-green-600" />
              </div>
            )}
            {status === "error" && (
              <div className="rounded-full bg-red-100 p-3">
                <AlertCircle className="h-12 w-12 text-red-600" />
              </div>
            )}
          </div>

          {status === "processing" && (
            <>
              <p className="text-center text-sm text-muted-foreground">
                Processing your account setup
              </p>
              <div className="rounded-md bg-muted p-4">
                <h4 className="mb-2 text-sm font-medium">What's happening?</h4>
                <ul className="space-y-2 text-sm">
                  {/* Main steps */}
                  {Object.entries(step_status)
                    .filter(([key]) => !key.includes('substeps'))
                    .map(([key, value]) => (
                      <li key={key} className="flex items-center">
                        {value === "completed" ? (
                          <CheckCircle className="mr-2 h-4 w-4 text-green-600" />
                        ) : value === "error" ? (
                          <AlertCircle className="mr-2 h-4 w-4 text-red-600" />
                        ) : (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin text-muted-foreground" />
                        )}
                        <span>Step {key.replace('step', '')}: {value === "completed" ? "Complete" : value === "error" ? "Failed" : "Processing"}</span>
                      </li>
                    ))
                  }

                  {/* Substeps if they exist */}
                  {step_status.step1_substeps && (
                    <li className="mt-2">
                      <p className="font-medium mb-1">Substeps:</p>
                      <ul className="space-y-1 pl-6">
                        {Object.entries(step_status.step1_substeps).map(([key, value]) => (
                          <li key={key} className="flex items-center">
                            {value === "completed" ? (
                              <CheckCircle className="mr-2 h-3 w-3 text-green-600" />
                            ) : value === "error" ? (
                              <AlertCircle className="mr-2 h-3 w-3 text-red-600" />
                            ) : (
                              <Loader2 className="mr-2 h-3 w-3 animate-spin text-muted-foreground" />
                            )}
                            <span className="text-xs">Substep {key.replace('substep', '')}</span>
                          </li>
                        ))}
                      </ul>
                    </li>
                  )}
                </ul>
              </div>
            </>
          )}

          {errorMessage && status === "error" && (
            <div className="rounded-md bg-destructive/15 p-4 text-sm text-destructive">
              <p className="font-medium">Error:</p>
              <p>{errorMessage}</p>
            </div>
          )}
        </CardContent>
        <CardFooter className="flex flex-col space-y-2">
          {status === "completed" && (
            <Button className="w-full" onClick={() => window.location.href = "/"}>
              Go to Dashboard
            </Button>
          )}

          {status === "error" && (
            <Button className="w-full" onClick={handleManualCheck} variant="outline">
              <RefreshCw className="mr-2 h-4 w-4" />
              Retry
            </Button>
          )}

          {status === "processing" && (
            <p className="text-xs text-center text-muted-foreground">
              This process may take some time. You can close this window and check back later.
            </p>
          )}
        </CardFooter>
      </Card>
    </div>
  )
}
