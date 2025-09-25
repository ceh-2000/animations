using System.Collections.Generic;
using Oculus.Interaction;
using Oculus.Interaction.Input;
using UnityEngine;
using Object = UnityEngine.Object;


public class GeneralHandManager : MonoBehaviour
{
    [SerializeField] [Interface(typeof(IHand))]
    private Object _leftHand; // Left hand reference

    [SerializeField] [Interface(typeof(IHand))]
    private Object _rightHand; // Right hand reference

    public HandCollisionListener leftHandCollisionListener; // Listen for left hand collisions
    public HandCollisionListener rightHandCollisionListener; // Listen for right hand collisions

    public OVRHand leftHand;
    public OVRHand rightHand;
    public GameObject ovrLeftHand;
    public GameObject ovrRightHand;
    private bool _isLeftHandPinching; // Whether left hand is pinching
    private bool _isRightHandPinching; // Whether right hand is pinching
    private List<GameObject> _leftInteractableObjects;
    private Vector3 _leftPinchPosition; // Vector3 for left pinch position
    private PinchState _leftPinchState; // Track pinch states for left hand

    private Vector3 _leftStartPinchPosition; // Vector3 for start left pinch position
    private List<GameObject> _rightInteractableObjects;
    private Vector3 _rightPinchPosition; // Vector3 for right pinch position
    private PinchState _rightPinchState; // Track pinch states for right hand
    private Vector3 _rightStartPinchPosition; // Vector3 for start right pinch position

    // Hand references
    public IHand LeftHand { get; private set; }
    public IHand RightHand { get; private set; }

    private void Start()
    {
        LeftHand = _leftHand as IHand;
        RightHand = _rightHand as IHand;
        _isLeftHandPinching = false;
        _isRightHandPinching = false;
        _leftStartPinchPosition = new Vector3(0, 0, 0);
        _rightStartPinchPosition = new Vector3(0, 0, 0);
        _leftPinchPosition = new Vector3(0, 0, 0);
        _rightPinchPosition = new Vector3(0, 0, 0);
        _leftPinchState = PinchState.None;
        _rightPinchState = PinchState.None;
        _leftInteractableObjects = null;
        _rightInteractableObjects = null;
    }

    // Update is called once per frame
    private void Update()
    {
        DetectPinch(LeftHand, ref _isLeftHandPinching, ref _leftStartPinchPosition, ref _leftPinchPosition,
            ref _leftPinchState, "Left Hand");
        DetectPinch(RightHand, ref _isRightHandPinching, ref _rightStartPinchPosition, ref _rightPinchPosition,
            ref _rightPinchState, "Right Hand");
        _leftInteractableObjects = DetectCollisions(leftHandCollisionListener);
        _rightInteractableObjects = DetectCollisions(rightHandCollisionListener);
    }

    private void DetectPinch(IHand hand, ref bool isPinching, ref Vector3 startPinchPosition,
        ref Vector3 pinchPosition,
        ref PinchState pinchState, string handName)
    {
        if (hand == null) return;

        var isPinchingNow = hand.GetFingerIsPinching(HandFinger.Index);

        // Pinch down
        Pose thumbTipPose, indexTipPose;
        if (isPinchingNow && !isPinching)
        {
            pinchState = PinchState.PinchDown;
            isPinching = true;

            // Determine the average position of the pinch start
            if (hand.GetJointPose(HandJointId.HandThumbTip, out thumbTipPose) &&
                hand.GetJointPose(HandJointId.HandIndexTip, out indexTipPose))
            {
                startPinchPosition = (thumbTipPose.position + indexTipPose.position) / 2;
                pinchPosition = startPinchPosition;
            }
        }

        // Pinch up
        else if (!isPinchingNow && isPinching)
        {
            pinchState = PinchState.PinchUp;

            // Reset values
            isPinching = false;
            startPinchPosition = new Vector3(0, 0, 0);
            pinchPosition = new Vector3(0, 0, 0);
        }

        // Pinch continued
        else if (isPinching)
        {
            pinchState = PinchState.Pinching;

            // Determine the average position of the continued pinch
            if (hand.GetJointPose(HandJointId.HandThumbTip, out thumbTipPose) &&
                hand.GetJointPose(HandJointId.HandIndexTip, out indexTipPose))
                pinchPosition = (thumbTipPose.position + indexTipPose.position) / 2;
        }

        // No change from not pinching
        else if (!isPinchingNow && !isPinching)
        {
            pinchState = PinchState.None;
        }
    }

    private List<GameObject> DetectCollisions(HandCollisionListener handCollisionListener)
    {
        return handCollisionListener.GetCollidedObjects();
    }

    public PinchState GetPinchState(string handName)
    {
        if (handName == "left") return _leftPinchState;

        if (handName == "right") return _rightPinchState;

        Debug.LogError($"{handName} is not a valid hand name.");
        return PinchState.None;
    }

    public Vector3 GetStartPinchPosition(string handName)
    {
        if (handName == "left") return _leftStartPinchPosition;

        if (handName == "right") return _rightStartPinchPosition;

        Debug.LogError($"{handName} is not a valid hand name.");
        return new Vector3(0, 0, 0);
    }

    public Vector3 GetPinchPosition(string handName)
    {
        if (handName == "left") return _leftPinchPosition;

        if (handName == "right") return _rightPinchPosition;

        Debug.LogError($"{handName} is not a valid hand name.");
        return new Vector3(0, 0, 0);
    }

    public List<GameObject> GetInteractableObject(string handName)
    {
        if (handName == "left") return _leftInteractableObjects;

        if (handName == "right") return _rightInteractableObjects;

        Debug.LogError($"{handName} is not a valid hand name.");
        return null;
    }

    public Vector3 GetHandPosition(string handName)
    {
        if (handName == "left") return leftHand.transform.position;
        if (handName == "right") return rightHand.transform.position;
        Debug.LogError($"{handName} is not a valid hand name.");
        return Vector3.zero;
    }

    public Vector3 GetIndexTipPosition(string handName)
    {
        Pose indexTipPose;
        if (handName == "left")
        {
            if (LeftHand.GetJointPose(HandJointId.HandIndexTip, out indexTipPose)) return indexTipPose.position;
        }
        else if (handName == "right")
        {
            if (RightHand.GetJointPose(HandJointId.HandIndexTip, out indexTipPose)) return indexTipPose.position;
        }

        Debug.LogError($"{handName} is not a valid hand name.");
        return Vector3.zero;
    }

    public void SetHandMaterial(string handName, Material material)
    {
        if (handName == "left")
        {
            var leftHandRenderer = ovrLeftHand.GetComponent<Renderer>();
            if (leftHandRenderer != null) leftHandRenderer.material = material;
        }
        else if (handName == "right")
        {
            var rightHandRenderer = ovrRightHand.GetComponent<Renderer>();
            if (rightHandRenderer != null) rightHandRenderer.material = material;
        }
        else
        {
            Debug.LogError($"{handName} is not a valid hand name.");
        }
    }

    public void ClearObjectCollisions()
    {
        leftHandCollisionListener.ClearCollidedObjects();
        rightHandCollisionListener.ClearCollidedObjects();
    }
}