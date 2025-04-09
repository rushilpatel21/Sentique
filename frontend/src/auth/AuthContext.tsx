import { useEffect, createContext, useState } from 'react'
import { getAuth, getConfig } from '@/auth/allAuth.tsx'

export const AuthContext = createContext<any>(null)

function Loading() {
    return <div>Starting...</div>
}

function LoadingError() {
    return <div>Loading error!</div>
}

export function AuthContextProvider(props: any) {
    const [auth, setAuth] = useState<any>(undefined)
    const [config, setConfig] = useState<any>(undefined)

    useEffect(() => {
        function onAuthChanged(e: any): void {
            setAuth((auth: any) => {
                if (typeof auth === 'undefined') {
                    console.log('Authentication status loaded')
                } else {
                    console.log('Authentication status updated')
                }
                return e.detail
            })
        }

        document.addEventListener('allauth.auth.change', onAuthChanged)
        getAuth().then((data: any) => setAuth(data)).catch((e: any) => {
            console.error(e)
            setAuth(false)
        })
        getConfig().then((data: any) => setConfig(data)).catch((e: any) => {
            console.error(e)
        })
        return () => {
            document.removeEventListener('allauth.auth.change', onAuthChanged)
        }
    }, [])

    const loading = (typeof auth === 'undefined') || config?.status !== 200
    return (
        <AuthContext.Provider value={{ auth, config }}>
            {loading
                ? <Loading />
                : (auth === false
                    ? <LoadingError />
                    : props.children)}
        </AuthContext.Provider>
    )
}
