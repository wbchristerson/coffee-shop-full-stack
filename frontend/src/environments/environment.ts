export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-9xo5gdfc.us', // the auth0 domain prefix
    audience: 'coffee', // the audience set for the auth0 app
    clientId: '3TS9Jrdx4jSTQJsm66KxdNkoxUseCd0p', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
