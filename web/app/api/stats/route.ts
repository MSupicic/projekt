import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET() {
    const total = await prisma.log.count();
    const suspicious = await prisma.log.count({
        where: { prediction_label: 'Suspicious' }
    });
    const normal = await prisma.log.count({
        where: { prediction_label: 'Normal' }
    });

    // Last update time
    const lastLog = await prisma.log.findFirst({
        orderBy: { timestamp: 'desc' }
    });

    return NextResponse.json({
        total,
        suspicious,
        normal,
        lastUpdate: lastLog?.timestamp || new Date()
    });
}
