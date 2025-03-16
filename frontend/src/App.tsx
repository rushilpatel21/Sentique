import {AuthContextProvider} from "@/auth";
import Router from "@/routes/Routes.tsx";
import {ThemeProvider} from "@/components/theme-provider.tsx";
function App() {

  return (
      <AuthContextProvider>
          <ThemeProvider>
            <Router/>
          </ThemeProvider>
      </AuthContextProvider>
  )
}

export default App
