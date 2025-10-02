/**
 * GitHub OAuth helper using the OAuth Device Flow.
 *
 * The implementation relies on Axios to request a device code and
 * exchange it for an access token.  This flow avoids the need for a
 * callback URL and works well in CLI demos.
 */
let axios;

try {
  axios = require('axios');
} catch (error) {
  throw new Error("The 'axios' package is required. Install it with 'npm install axios'.");
}

const DEVICE_CODE_URL = 'https://github.com/login/device/code';
const TOKEN_URL = 'https://github.com/login/oauth/access_token';

async function requestDeviceCode(clientId, scope = 'repo read:user') {
  const response = await axios.post(
    DEVICE_CODE_URL,
    new URLSearchParams({ client_id: clientId, scope }).toString(),
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json' } },
  );

  return response.data;
}

async function pollForToken({ clientId, deviceCode, interval = 5 }) {
  while (true) {
    await new Promise((resolve) => setTimeout(resolve, interval * 1000));

    const response = await axios.post(
      TOKEN_URL,
      new URLSearchParams({
        client_id: clientId,
        device_code: deviceCode,
        grant_type: 'urn:ietf:params:oauth:grant-type:device_code',
      }).toString(),
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json' } },
    );

    if (response.data.access_token) {
      return response.data;
    }

    if (response.data.error !== 'authorization_pending') {
      throw new Error(`OAuth flow failed: ${response.data.error_description || response.data.error}`);
    }
  }
}

module.exports = { requestDeviceCode, pollForToken };

if (require.main === module) {
  const clientId = process.env.GITHUB_CLIENT_ID;
  if (!clientId) {
    console.error('Set GITHUB_CLIENT_ID to run the OAuth device flow demo.');
    process.exit(1);
  }

  requestDeviceCode(clientId)
    .then((data) => {
      console.log('Visit the verification URI and enter the code:', data.verification_uri, data.user_code);
      return pollForToken({ clientId, deviceCode: data.device_code, interval: data.interval });
    })
    .then((tokenInfo) => {
      console.log('Token received:', tokenInfo.token_type);
    })
    .catch((error) => {
      console.error(error.message);
    });
}
