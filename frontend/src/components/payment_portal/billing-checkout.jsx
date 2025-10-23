import React, { useCallback, useState, useEffect } from "react";
import stripePromise from '../../services/stripeClient';
import {
  EmbeddedCheckoutProvider,
  EmbeddedCheckout
} from '@stripe/react-stripe-js';
import { Navigate } from "react-router-dom";

// Make sure to call `loadStripe` outside of a component’s render to avoid
// recreating the `Stripe` object on every render.
// `stripePromise` is exported from src/services/stripeClient.js and uses
// NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY environment variable when available.

const CheckoutForm = () => {
  const [clientSecret, setClientSecret] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Prefetch the client secret so we can show a loading/status UI while the
  // EmbeddedCheckout component initializes. If the backend is unreachable this
  // makes the problem visible instead of rendering an empty area.
  useEffect(() => {
    let mounted = true;
    setLoading(true);
    fetch(`http://localhost:8000/api/payments/create-checkout-session`, {
      method: "POST",
      headers: { 'Content-Type': 'application/json' }
    })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (!mounted) return;
        if (!data || !data.clientSecret) {
          setError('No clientSecret returned from server');
        } else {
          setClientSecret(data.clientSecret);
        }
      })
      .catch((err) => {
        if (!mounted) return;
        setError(err.message || String(err));
      })
      .finally(() => {
        if (!mounted) return;
        setLoading(false);
      });

    return () => { mounted = false };
  }, []);

  if (loading) {
    return (
      <div id="checkout" style={{ minHeight: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px dashed #ccc', borderRadius: 8 }}>
        <div>Loading checkout...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div id="checkout" style={{ minHeight: 200, padding: 16, border: '1px solid #f00', borderRadius: 8 }}>
        <strong>Unable to load checkout</strong>
        <div style={{ marginTop: 8, color: '#900' }}>{error}</div>
        <div style={{ marginTop: 8 }}>
          Confirm your backend is running at <code>http://localhost:8000</code> and the endpoint <code>/api/payment_portal/create-checkout-session</code> returns a JSON object with <code>clientSecret</code>.
        </div>
      </div>
    );
  }

  // When we have a clientSecret, render the embedded checkout.
  const options = { clientSecret };

  return (
    <div id="checkout" style={{ minHeight: 400 }}>
      <EmbeddedCheckoutProvider
        stripe={stripePromise}
        options={options}
      >
        <EmbeddedCheckout />
      </EmbeddedCheckoutProvider>
    </div>
  )
}

const Return = () => {
  const [status, setStatus] = useState(null);
  const [customerEmail, setCustomerEmail] = useState('');

  useEffect(() => {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const sessionId = urlParams.get('session_id');
    if (!sessionId) return;

    fetch(`http://localhost:8000/api/payments/session-status?session_id=${sessionId}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setStatus(data.status);
        setCustomerEmail(data.customer_email);
      })
      .catch((err) => {
        console.error('Failed to fetch session status', err);
      });
  }, []);

  if (status === 'open') {
    return (
      <Navigate to="/checkout" />
    )
  }

  if (status === 'complete') {
    return (
      <section id="success">
        <p>
          We appreciate your business! A confirmation email will be sent to {customerEmail}.

          If you have any questions, please email <a href="mailto:orders@example.com">orders@example.com</a>.
        </p>
      </section>
    )
  }

  return null;
}

export { Return };
export default CheckoutForm;

