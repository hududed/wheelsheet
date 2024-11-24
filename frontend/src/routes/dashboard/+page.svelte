<script lang="ts">
  import * as Card from "$lib/components/ui/card";
  import { columns, type Order } from './columns';
  import DataTable from './data-table.svelte';

  // Export the data prop
  export let data: { orders: Order[] }; 
</script>

<Card.Root>
  <Card.Header>
    <Card.Title>Order History</Card.Title>
  </Card.Header>
  <Card.Content>
    {#if data.orders.length > 0}
      <DataTable data={data.orders} columns={columns} />
    {:else}
      <p>No orders available.</p>
    {/if}
  </Card.Content>
</Card.Root>