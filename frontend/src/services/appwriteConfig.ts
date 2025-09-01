import { Client, Account } from 'appwrite';

export const client = new Client();

client
    .setEndpoint('https://fra.cloud.appwrite.io/v1') // Your API Endpoint
    .setProject('68ae10d10003d98c852e'); // Your project ID

export const account = new Account(client);

export const GOOGLE_OAUTH_CONFIG = {
    clientId: '859880898609-cfi5h8i4v4v238gonouulu4u5vqqjc0v.apps.googleusercontent.com',
    redirectUri: 'https://fra.cloud.appwrite.io/v1/account/sessions/oauth2/callback/google/68ae10d10003d98c852e'
};
