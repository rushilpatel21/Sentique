import {useState, useEffect, JSX} from 'react'
import { AuthChangeRedirector, AnonymousRoute, AuthenticatedRoute } from '@/auth'
import {
    createBrowserRouter,
    RouterProvider,
    RouteObject, Outlet
} from 'react-router-dom'

import { useConfig } from '@/auth'
import ROUTES from './route.ts'
import {Home} from "@/pages/Home.tsx";
import Login from "@/pages/Auth/Login.tsx";
import Register from "@/pages/Auth/Register.tsx";
import Layout from "@/Layout/Layout.tsx";

// Page Components

// Router Setup
function createRouter(): ReturnType<typeof createBrowserRouter> {
const routes: RouteObject[] = [
    {
        path: ROUTES.HOME,
        element: <AuthChangeRedirector><Outlet/></AuthChangeRedirector>,
        children: [
            // Authentication routes without layout
            {path: ROUTES.LOGIN, element: <AnonymousRoute><Login/></AnonymousRoute>},
            {path: ROUTES.REGISTER, element: <AnonymousRoute><Register/></AnonymousRoute>},

            // All other routes with layout
            {
                element: <Layout><Outlet/></Layout>,
                children: [
                    {path: ROUTES.HOME, element: <AuthenticatedRoute><Home/></AuthenticatedRoute>},
                ]
            }
        ]
    }
];

    return createBrowserRouter(routes);
}


export default function Router(): JSX.Element | null {
    const [router, setRouter] = useState<ReturnType<typeof createBrowserRouter> | null>(null);
    const config = useConfig();

    useEffect(() => {
        setRouter(createRouter());
    }, [config]);

    return router ? <RouterProvider router={router} /> : null;
}
