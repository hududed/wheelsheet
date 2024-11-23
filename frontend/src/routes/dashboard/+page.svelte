<script lang="ts">
  import * as Card from "$lib/components/ui/card";
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';

  let orders = writable([]);
  let error = writable('');

  onMount(async () => {
    const response = await fetch('http://localhost:8000/api/fetch_robinhood_orders', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username: 'your_username', password: 'your_password' }) // Replace with actual credentials
    });

    if (response.ok) {
      const data = await response.json();
      orders.set(data.orders);

      // Insert orders into Supabase
      await fetch('http://localhost:8000/api/insert_orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data.orders)
      });
    } else {
      const errorData = await response.json();
      error.set(errorData.error || 'Failed to fetch order history');
    }
  });
</script>

<Card.Root>
  <Card.Header>
    <Card.Title>Order History</Card.Title>
  </Card.Header>
  <Card.Content>
    {#if $error}
      <p class="text-red-500">{ $error }</p>
    {/if}
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Instrument</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">State</th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        {#each $orders as order}
          <tr>
            <td class="px-6 py-4 whitespace-nowrap">{order.instrument}</td>
            <td class="px-6 py-4 whitespace-nowrap">{order.quantity}</td>
            <td class="px-6 py-4 whitespace-nowrap">{order.price}</td>
            <td class="px-6 py-4 whitespace-nowrap">{order.state}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </Card.Content>
</Card.Root>