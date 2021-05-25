﻿// Copyright 2021 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.


using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// <c>Enemy</c> A simple npc designed to move and attack the player.
/// </summary>
public class Enemy : MonoBehaviour
{
    [Tooltip("Distance at which to start attacking the player.")]
    [Range(1, 100)]
    public float activationRange = 10f;
    [Tooltip("Duration of the firing phase of the attack.")]
    [Range(0, 100)]
    public float attackDuration = 5f;
    [Tooltip("Duration of the hiding/waiting phase of the attack.")]
    [Range(0, 100)]
    public float hideDuration = 5f;

    private Vector3 initialPosition;
    private Vector3 attackPosition;
    private Weapon weapon;

    private static List<Enemy> enemies = new List<Enemy>();

    /// <summary>
    /// Returns a list of all enabled Enemies in the world.
    /// </summary>
    public static List<Enemy> Enemies { get { return enemies; } }

    void OnEnable() {
        enemies.Add(this);
        initialPosition = transform.position;
        attackPosition = transform.position + transform.right * 2f;
        weapon = GetComponent<Weapon>();
    }

    void OnDisable() {
        enemies.Remove(this);
    }

    IEnumerator Start() {
        yield return StartCoroutine(Attack());
    }

    /// <summary>
    /// Defines a very simple attack sequence.
    /// </summary>
    IEnumerator Attack() {
        while (true) {
            FirstPersonPlayer player = GetPlayer();
            if (player && Vector3.Distance(
                player.transform.position, transform.position) <= activationRange) {
                yield return Move(attackPosition, 1f);
                yield return Fire(attackDuration);
                yield return Move(initialPosition, 1f);
                yield return Wait(hideDuration);
            } else {
                yield return new WaitForFixedUpdate();
            }
        }
    }

    /// <summary>
    /// Moves the Enemy from one position to another.
    /// </summary>
    IEnumerator Move(Vector3 goalPos, float moveTime) {
        Vector3 startingPos  = transform.position;
        float elapsedTime = 0;
        while (elapsedTime < moveTime)
        {
            transform.position = Vector3.Lerp(startingPos, goalPos, (elapsedTime / moveTime));
            elapsedTime += Time.fixedDeltaTime;
            yield return new WaitForFixedUpdate();
        }
    }

    /// <summary>
    /// Fires at the player for the specified amount of time.
    /// </summary>
    IEnumerator Fire(float duration) {
        FirstPersonPlayer player = GetPlayer();
        float elapsedTime = 0;
        while (elapsedTime < duration)
        {
            if (player) {
                weapon.Fire(player.gameObject, player.transform.position + new Vector3(0,1,0));
            }
            elapsedTime += Time.fixedDeltaTime;
            yield return new WaitForFixedUpdate();
        }
    }

    /// <summary>
    /// Waits for a specified amount of time.
    /// </summary>
    IEnumerator Wait(float duration) {
        float elapsedTime = 0;
        while (elapsedTime < duration)
        {
            elapsedTime += Time.fixedDeltaTime;
            yield return new WaitForFixedUpdate();
        }
    }

    /// <summary>
    /// Returns the current FirstPersonPlayer instance.
    /// </summary>
    private FirstPersonPlayer GetPlayer() {
        return FirstPersonPlayer.Players.Count > 0 ? FirstPersonPlayer.Players[0] : null;
    }
}