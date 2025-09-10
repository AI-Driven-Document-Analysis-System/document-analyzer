"use client"

import { useState } from 'react'
import './subscription.css'

// Add keyframes for floating animation
const floatingAnimation = `
  @keyframes float {
    0%, 100% { transform: translateY(0) translateX(-50%); }
    50% { transform: translateY(-10px) translateX(-50%); }
  }
`

interface PricingTier {
  name: string
  price: string
  period: string
  description: string
  features: string[]
  buttonText: string
  buttonVariant: 'primary' | 'secondary' | 'premium'
  popular?: boolean
}

const pricingTiers: PricingTier[] = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Perfect for getting started",
    features: [
      "5 documents per month",
      "Basic OCR processing",
      "Standard chat queries",
      "Document upload up to 10MB",
      "Basic analytics",
      "Email support"
    ],
    buttonText: "Get Started Free",
    buttonVariant: "secondary"
  },
  {
    name: "Pro",
    price: "$29",
    period: "per month",
    description: "For professionals and small teams",
    features: [
      "500 documents per month",
      "Advanced AWS Textract OCR",
      "Unlimited chat queries",
      "Document upload up to 50MB",
      "Advanced analytics & insights",
      "Priority email support",
      "Document summarization",
      "Batch processing",
      "API access"
    ],
    buttonText: "Upgrade to Pro",
    buttonVariant: "primary",
    popular: true
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "contact us",
    description: "For large organizations",
    features: [
      "Unlimited documents",
      "Enterprise-grade OCR",
      "Custom AI models",
      "Unlimited file size",
      "Advanced security & compliance",
      "24/7 phone support",
      "Custom integrations",
      "On-premise deployment",
      "Dedicated account manager",
      "SLA guarantees"
    ],
    buttonText: "Contact Sales",
    buttonVariant: "premium"
  }
]

export function Subscription() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly')

  const handleUpgrade = (tierName: string) => {
    if (tierName === 'Free') {
      console.log('Starting with free tier')
    } else if (tierName === 'Pro') {
      console.log('Upgrading to Pro')
    } else if (tierName === 'Enterprise') {
      console.log('Contacting sales for Enterprise')
    }
  }

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: floatingAnimation }} />
      <div className="subscription-container">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          {/* Header */}
          <div className="text-center mb-16">
            <h1 className="gradient-title">
              Simple, Transparent Pricing
            </h1>
          </div>

          {/* Pricing Cards */}
          <div className="pricing-cards-container">
            {pricingTiers.map((tier) => (
              <div
                key={tier.name}
                className={`pricing-card ${tier.popular ? 'popular' : ''}`}
              >
                {tier.popular && (
                  <div className="popular-badge">
                    Most Popular
                  </div>
                )}

                <div className="pricing-header">
                  <h3>{tier.name}</h3>
                  <div className="price">
                    <span className="amount">{tier.price}</span>
                    <span className="period">/{tier.period}</span>
                  </div>
                  <p className="description">{tier.description}</p>
                </div>

                <div className="features">
                  <ul>
                    {tier.features.map((feature, index) => (
                      <li key={index}>
                        <svg className="check-icon" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <button
                  onClick={() => handleUpgrade(tier.name)}
                  className={`pricing-button ${tier.buttonVariant}`}
                >
                  {tier.buttonText}
                </button>
              </div>
            ))}
          </div>

          {/* FAQ Section */}
          <div className="faq-section">
            <h3>Frequently Asked Questions</h3>
            <div className="faq-grid">
              {[
                {
                  q: "Can I change my plan anytime?",
                  a: "Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately."
                },
                {
                  q: "What payment methods do you accept?",
                  a: "We accept all major credit cards, PayPal, and bank transfers for enterprise plans."
                },
                {
                  q: "Is there a free trial?",
                  a: "Yes, all paid plans come with a 14-day free trial. No credit card required."
                },
                {
                  q: "What happens to my documents if I downgrade?",
                  a: "Your documents remain safe. You'll just have reduced processing limits going forward."
                }
              ].map((faq, i) => (
                <div key={i} className="faq-item">
                  <h4>{faq.q}</h4>
                  <p>{faq.a}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Enterprise CTA */}
          <div className="enterprise-cta">
            <h3>Need a custom solution?</h3>
            <p>
              Contact our sales team for enterprise pricing and custom features tailored to your organization.
            </p>
            <button className="contact-sales-btn">
              <svg className="phone-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.54 1.06l-1.518.759a11.042 11.042 0 006.105 6.105l.759-1.518a1 1 0 011.06-.54l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              Contact Sales Team
            </button>
          </div>
        </div>
      </div>
    </>
  )
}