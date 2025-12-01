'use client';

import { ErrorPage } from '@/components/pages/ErrorPage';

export default function AppError({
  error
}: {
  error: Error & { digest?: string };
}) {

  return <ErrorPage error={error} />;
}