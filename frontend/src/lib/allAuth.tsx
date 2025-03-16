import { getCSRFToken } from './cerfToken.ts'
import {Register, Login} from "@/types/forms.ts";

const Client = Object.freeze({
    APP: 'app',
    BROWSER: 'browser'
} as const)

type ClientType = typeof Client[keyof typeof Client]

const CLIENT: ClientType = Client.BROWSER

const BASE_URL: string = `/api/${CLIENT}/v1`
const ACCEPT_JSON: { accept: string } = {
    accept: 'application/json'

}

export const AuthProcess = Object.freeze({
    LOGIN: 'login',
    CONNECT: 'connect'
} as const)

export const Flows = Object.freeze({
    VERIFY_EMAIL: 'verify_email',
    LOGIN: 'login',
    LOGIN_BY_CODE: 'login_by_code',
    SIGNUP: 'signup',
    PROVIDER_REDIRECT: 'provider_redirect',
    PROVIDER_SIGNUP: 'provider_signup',
    MFA_AUTHENTICATE: 'mfa_authenticate',
    REAUTHENTICATE: 'reauthenticate',
    MFA_REAUTHENTICATE: 'mfa_reauthenticate',
    MFA_WEBAUTHN_SIGNUP: 'mfa_signup_webauthn'
} as const)

export const URLs: { [key: string]: string } = Object.freeze({
    // Meta
    CONFIG: BASE_URL + '/config',

    // Account management
    CHANGE_PASSWORD: BASE_URL + '/account/password/change',
    EMAIL: BASE_URL + '/account/email',
    PROVIDERS: BASE_URL + '/account/providers',

    // Account management: 2FA
    AUTHENTICATORS: BASE_URL + '/account/authenticators',
    RECOVERY_CODES: BASE_URL + '/account/authenticators/recovery-codes',
    TOTP_AUTHENTICATOR: BASE_URL + '/account/authenticators/totp',

    // Auth: Basics
    LOGIN: BASE_URL + '/auth/login',
    REQUEST_LOGIN_CODE: BASE_URL + '/auth/code/request',
    CONFIRM_LOGIN_CODE: BASE_URL + '/auth/code/confirm',
    SESSION: BASE_URL + '/auth/session',
    REAUTHENTICATE: BASE_URL + '/auth/reauthenticate',
    REQUEST_PASSWORD_RESET: BASE_URL + '/auth/password/request',
    RESET_PASSWORD: BASE_URL + '/auth/password/reset',
    SIGNUP: BASE_URL + '/auth/signup',
    VERIFY_EMAIL: BASE_URL + '/auth/email/verify',

    // Auth: 2FA
    MFA_AUTHENTICATE: BASE_URL + '/auth/2fa/authenticate',
    MFA_REAUTHENTICATE: BASE_URL + '/auth/2fa/reauthenticate',

    // Auth: Social
    PROVIDER_SIGNUP: BASE_URL + '/auth/provider/signup',
    REDIRECT_TO_PROVIDER: BASE_URL + '/auth/provider/redirect',
    PROVIDER_TOKEN: BASE_URL + '/auth/provider/token',

    // Auth: Sessions
    SESSIONS: BASE_URL + '/auth/sessions',

    USERMETA: 'http://localhost:10000/_allauth/api/profile/',

    // Auth: WebAuthn
    REAUTHENTICATE_WEBAUTHN: BASE_URL + '/auth/webauthn/reauthenticate',
    AUTHENTICATE_WEBAUTHN: BASE_URL + '/auth/webauthn/authenticate',
    LOGIN_WEBAUTHN: BASE_URL + '/auth/webauthn/login',
    SIGNUP_WEBAUTHN: BASE_URL + '/auth/webauthn/signup',
    WEBAUTHN_AUTHENTICATOR: BASE_URL + '/account/authenticators/webauthn'
})

export const AuthenticatorType = Object.freeze({
    TOTP: 'totp',
    RECOVERY_CODES: 'recovery_codes',
    WEBAUTHN: 'webauthn'
} as const)

function postForm(action: string, data: { [key: string]: string }): void {
    const f = document.createElement('form')
    f.method = 'POST'
    f.action = action

    for (const key in data) {
        const d = document.createElement('input')
        d.type = 'hidden'
        d.name = key
        d.value = data[key]
        f.appendChild(d)
    }
    document.body.appendChild(f)
    f.submit()
}

const tokenStorage: Storage = window.sessionStorage

export async function request(
    method: string,
    path: string,
    data?: any,
    headers?: { [key: string]: string }
): Promise<never> {
    const options: RequestInit = {
        method,
        headers: {
            ...ACCEPT_JSON,
            ...headers
        }
    }
    options.credentials = 'include'
    if (path !== URLs.CONFIG) {
        if (CLIENT === Client.BROWSER) {
            options.headers['X-CSRFToken'] = getCSRFToken()

        } else if (CLIENT === Client.APP) {
            options.headers['User-Agent'] = 'django-allauth example app'
            const sessionToken = tokenStorage.getItem('sessionToken')
            if (sessionToken) {
                options.headers['X-Session-Token'] = sessionToken
            }
        }
    }

    if (typeof data !== 'undefined') {
        options.body = JSON.stringify(data)
        options.headers['Content-Type'] = 'application/json'
    }

    const resp = await fetch(path, options);

    // Check if response body exists and if content-type is JSON
    const contentType = resp.headers.get("content-type");
    const hasBody = resp.headers.has("content-length") && parseInt(resp.headers.get("content-length") || "0") > 0;

    let msg = null;
    if (hasBody && contentType && contentType.includes("application/json")) {
        try {
            msg = await resp.json();
        } catch (error) {
            console.error("Failed to parse JSON response:", error);
        }
    }

    // Handle cases when msg is null or empty
    if (msg?.status === 410) {
        tokenStorage.removeItem('sessionToken');
    }
    if (msg?.meta?.session_token) {
        tokenStorage.setItem('sessionToken', msg.meta.session_token);
    }
    if (msg && ([401, 410].includes(msg.status) || (msg.status === 200 && msg.meta?.is_authenticated) || msg.key)) {
        const event = new CustomEvent('allauth.auth.change', { detail: msg });
        document.dispatchEvent(event);
    }

    return msg;  // Return msg even if it's null to avoid unexpected crashes

}

// API Functions
export async function login(data: Login): Promise<never> {
    return await request('POST', URLs.LOGIN, data)
}

export async function register(data: Register): Promise<never> {
    return await request('POST', URLs.SIGNUP, data)
}

export async function logout(): Promise<never> {
    return await request('DELETE', URLs.SESSION)
}

export async function getConfig () {
    return await request('GET', URLs.CONFIG)
}

export async function getAuth () {
    return await request('GET', URLs.SESSION)
}

export function redirectToProvider (providerId:string , callbackURL:string, process = AuthProcess.LOGIN) {
    postForm(URLs.REDIRECT_TO_PROVIDER, {
        provider: providerId,
        process,
        callback_url: callbackURL,
        csrfmiddlewaretoken: getCSRFToken()
    })
}
