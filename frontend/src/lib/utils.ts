import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}



export const Client = Object.freeze({
    APP: 'app',
    BROWSER: 'browser'
} as const);

export type ClientType = typeof Client[keyof typeof Client];

export const CLIENT: ClientType = Client.BROWSER;

export const BASE_URL: string = `/api/${CLIENT}/v1`;