using System.Collections.Generic;
using UnityEngine;

public class HandCollisionListener : MonoBehaviour
{
    private HashSet<GameObject> collidedObjects = new();

    private void OnTriggerEnter(Collider other)
    {
        collidedObjects.Add(other.gameObject);
    }

    private void OnTriggerExit(Collider other)
    {
        if (collidedObjects.Contains(other.gameObject)) collidedObjects.Remove(other.gameObject);
    }

    private void OnTriggerStay(Collider other)
    {
        collidedObjects.Add(other.gameObject);
    }

    public List<GameObject> GetCollidedObjects()
    {
        return new List<GameObject>(collidedObjects);
    }

    public void ClearCollidedObjects()
    {
        collidedObjects = new HashSet<GameObject>();
    }
}