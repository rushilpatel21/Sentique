import {useState, useEffect, JSX} from 'react'
import { AuthChangeRedirector, AnonymousRoute, AuthenticatedRoute } from '@/auth'
import {
    createBrowserRouter,
    RouterProvider,
    RouteObject, Outlet
} from 'react-router-dom'

import { useConfig } from '@/auth'
import ROUTES from './route.ts'
import Login from "@/pages/Auth/Login.tsx";
import Register from "@/pages/Auth/Register.tsx";
import Layout from "@/Layout/Layout.tsx";

// Page Components
import {TrendAnalysis} from '@/pages/Trends/TrendAnalysis.tsx';
import Chat from "@/pages/Chatbot/Chat.tsx";
import {Dashboard} from "@/pages/Dashboard/Dashboard.tsx";
import {ViewReport} from "@/pages/Reports/ViewReport.tsx";
import {ProcessingPage} from "@/pages/Onboarding/processing-page.tsx";


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
            // Pending route
            {path: ROUTES.PENDING, element: <ProcessingPage/>},
            // All other routes with layout
            {
                element: <Layout><Outlet/></Layout>,
                children: [
                    {path: ROUTES.HOME, element: <AuthenticatedRoute><Dashboard/></AuthenticatedRoute>},
                    {path: ROUTES.CHAT, element: <AuthenticatedRoute><Chat/></AuthenticatedRoute> },
                    {path: ROUTES.TREND, element: <AuthenticatedRoute><TrendAnalysis/></AuthenticatedRoute> },
                    {path: ROUTES.VIEW_REPORT, element: <AuthenticatedRoute><ViewReport/></AuthenticatedRoute> }
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
