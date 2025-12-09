import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET() {
    // Aggregate logs by hour (simplified for now, usually done with raw SQL or group by)
    // Since Prisma groupByKey is limited, we might fetch recent data and aggregate in JS or use raw query

    // Taking last 1000 logs to chart
    const logs = await prisma.log.findMany({
        take: 1000,
        orderBy: { timestamp: 'asc' },
        select: { timestamp: true, prediction_label: true }
    });

    // Aggregate by minute/hour
    // Group by time interval
    const chartData = [];
    // ... implementation simplified: just return raw data for frontend to aggregate or pre-aggregated

    // For simplicity, let's group by "minute" here
    const grouped = logs.reduce((acc: any, log) => {
        const time = new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        if (!acc[time]) acc[time] = { time, suspicious: 0, normal: 0 };
        if (log.prediction_label === 'Suspicious') acc[time].suspicious++;
        else acc[time].normal++;
        return acc;
    }, {});

    return NextResponse.json(Object.values(grouped));
}
