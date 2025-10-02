/**
 * Prisma database adapter example.
 *
 * The helpers gracefully handle environments where `@prisma/client`
 * has not been generated yet by surfacing a descriptive runtime error.
 */
let PrismaClient;
let prismaModuleError;

try {
  ({ PrismaClient } = require('@prisma/client'));
} catch (error) {
  prismaModuleError = error;
}

function getClient() {
  if (!PrismaClient) {
    const message = [
      "@prisma/client is required for the Prisma adapter.",
      "Run 'npx prisma init' followed by 'npx prisma generate' and install the client with 'npm install @prisma/client'.",
    ].join(' ');
    const error = new Error(message);
    error.cause = prismaModuleError;
    throw error;
  }

  return new PrismaClient();
}

async function listUsers() {
  const client = getClient();
  try {
    return await client.user.findMany({ take: 5 });
  } finally {
    await client.$disconnect();
  }
}

module.exports = { getClient, listUsers };

if (require.main === module) {
  listUsers()
    .then((users) => {
      console.log('Sample users:', users);
    })
    .catch((error) => {
      console.error(error.message);
    });
}
