# ---------------------------------------------------------------------------
# Author:  John Hammond
# Date:    31OCT17
# Purpose: This script will determine which of the ESXi hosts has the most available
#          resources and offer it as the choice for a VMhost to create a new VM.
#
# ---------------------------------------------------------------------------


# USE Get-Datastore -RelatedObject ($vmhost) TO GET APPROPRIATE DATASTORE#

# Get the the most free space...
$most_free_space = (((Get-Datastore).FreeSpaceGB).ToDouble($null) | Measure -Maximum).Maximum

# Get the datastores with the most free space..
$free_datastores = ( Get-Datastore | Where { ($_.FreeSpaceGB).ToDouble($null) -eq $most_free_space } )
# If we have choices for hosts, start to look at which host has the most free memory.
[System.Collections.ArrayList]$most_free_memory = @()
ForEach ( $datastore In $free_datastores ){
    # Retrieve the hosts based off the datastore...
    $most_free_memory.Add( (Get-VMHost -Datastore $datastore) ) > $null
}
# Determine the most free memory of those hosts...
$minimum_memory = ((($most_free_memory).MemoryUsageGB).ToDouble($null) | Measure -Minimum).Minimum

# Now get the hosts with that most free memory..
$free_memory = ( $most_free_memory | Where { ($_.MemoryUsageGB).ToDouble($null) -eq $minimum_memory  } )

if ( $free_memory.Length -eq 1 ){ return $free_memory }

$minimum_cpu = ((($free_memory).CpuUsageMhz).ToDouble($null) | Measure -Minimum).Minimum

$free_cpu = ( $free_memory | Where { ($_.CpuUsageMhz).ToDouble($null) -eq $minimum_cpu  } )

if ( $free_cpu.Length -eq 1 ){ return $free_cpu }

# If there are many choices for the best machine to use, just pick one.
$best_choice = $free_cpu | Select -First 1
return ($best_choice)

# USE Get-Datastore -RelatedObject ($vmhost) TO GET APPROPRIATE DATASTORE