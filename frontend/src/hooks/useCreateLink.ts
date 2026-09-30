import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createLink } from '../api/links';

export function useCreateLink() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createLink,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['links'] });
    },
  });
}
