import { PrismaClient } from '@prisma/client'

const globalForPrisma = global as unknown as { prisma: PrismaClient }

console.log("Initializing Prisma Client...");
console.log("DATABASE_URL:", process.env.DATABASE_URL);

export const prisma = globalForPrisma.prisma || new PrismaClient({
    datasources: {
        db: {
            url: process.env.DATABASE_URL || "mysql://ids_user:ids_password@localhost:3307/ids_db",
        },
    },
})

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma
