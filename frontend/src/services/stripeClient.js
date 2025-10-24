import { loadStripe } from '@stripe/stripe-js'

// Use NEXT_PUBLIC_ env var so the key is exposed to the browser in Next/CRA builds
// Fallback to empty string if not set (loadStripe will return null)
const publishableKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || ''

export const stripePromise = publishableKey ? loadStripe(publishableKey) : null
export default stripePromise
