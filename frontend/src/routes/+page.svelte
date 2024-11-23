<script lang="ts">
  import { goto } from '$app/navigation';
  import * as Card from "$lib/components/ui/card";
  import { Input } from "$lib/components/ui/input";
  import { writable } from 'svelte/store';

  let username = '';
  let password = '';
  let mfaCode = '';
  let error = writable('');
  let showMfaInput = writable(false);

  async function loginRobinhood() {
    const response = await fetch('http://localhost:8000/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, password, mfa_code: mfaCode })
    });

    if (response.ok) {
      const data = await response.json();
      console.log(data);
      // Navigate to the dashboard
      goto('/dashboard');
    } else {
      const errorData = await response.json();
      if (errorData.error === "MFA required") {
        showMfaInput.set(true);
      } else {
        error.set(errorData.error || 'Failed to log in');
      }
    }
  }
</script>

<Card.Root>
  <Card.Header>
    <Card.Title>Robinhood Login</Card.Title>
  </Card.Header>
  <Card.Content>
    <form on:submit|preventDefault={loginRobinhood} class="space-y-4">
      <div>
        <Input type="text" bind:value={username} placeholder="Username" class="max-w-xs" />
      </div>
      <div>
        <Input type="password" bind:value={password} placeholder="Password" class="max-w-xs" />
      </div>
      {#if $showMfaInput}
        <div>
          <Input type="text" bind:value={mfaCode} placeholder="MFA Code" class="max-w-xs" />
        </div>
      {/if}
      <div>
        <input type="submit" value="Login to Robinhood" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
      </div>
      {#if $error}
        <p class="text-red-500">{ $error }</p>
      {/if}
    </form>
  </Card.Content>
</Card.Root>