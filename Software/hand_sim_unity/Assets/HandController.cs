using UnityEngine;

public class HandBoneController : MonoBehaviour
{
    public GloveReceiver receiver;

    [System.Serializable]
    public class FingerBones
    {
        [Header("Bones")]
        public Transform firstBone;
        public Transform secondBone;
        public Transform thirdBone;

        [Header("Current bend values")]
        [Range(0f, 120f)] public float firstAngle;
        [Range(0f, 120f)] public float secondAngle;
        [Range(0f, 120f)] public float thirdAngle;

        [Header("Rotation axis")]
        public FingerRotationAxis bendAxis = FingerRotationAxis.X;

        [Header("Invert")]
        public bool invertFirst;
        public bool invertSecond;
        public bool invertThird;

        [HideInInspector] public Quaternion firstStartRotation;
        [HideInInspector] public Quaternion secondStartRotation;
        [HideInInspector] public Quaternion thirdStartRotation;
    }

    public enum FingerRotationAxis
    {
        X,
        Y,
        Z
    }

    [Header("Thumb")]
    public FingerBones thumb;

    [Header("Index")]
    public FingerBones index;

    [Header("Middle")]
    public FingerBones middle;

    [Header("Ring")]
    public FingerBones ring;

    [Header("Pinky")]
    public FingerBones pinky;

    private void Start()
    {
        SaveStartRotations(thumb);
        SaveStartRotations(index);
        SaveStartRotations(middle);
        SaveStartRotations(ring);
        SaveStartRotations(pinky);
    }

    private void Update()
    {
		float bendthumb = receiver.fingerData[0];
		float bendindex = receiver.fingerData[1];
		float bendmiddle = receiver.fingerData[2];
		float bendring = receiver.fingerData[3];
		float bendpinky = receiver.fingerData[4];
		
		thumb.firstAngle = bendthumb ;
        index.firstAngle = bendindex ;
        middle.firstAngle = bendmiddle ;
        ring.firstAngle = bendring ;
        pinky.firstAngle = bendpinky ;

        thumb.secondAngle = Mathf.Max(0,bendthumb - 30f) ;
        index.secondAngle = Mathf.Max(0, bendindex -30f);
        middle.secondAngle = Mathf.Max(0, bendmiddle -30f);
        ring.secondAngle = Mathf.Max(0, bendring - 30f);
        pinky.secondAngle = Mathf.Max(0, bendpinky -30f);

        thumb.thirdAngle = Mathf.Max(0, bendthumb -60f);
        index.thirdAngle = Mathf.Max(0, bendindex -60f);
        middle.thirdAngle = Mathf.Max(0, bendmiddle -60f);
        ring.thirdAngle = Mathf.Max(0, bendring -60f);
        pinky.thirdAngle = Mathf.Max(0, bendpinky -60f) ;
		
        ApplyFingerRotation(thumb);
        ApplyFingerRotation(index);
        ApplyFingerRotation(middle);
        ApplyFingerRotation(ring);
        ApplyFingerRotation(pinky);
    }

    private void SaveStartRotations(FingerBones finger)
    {
        if (finger.firstBone != null)
            finger.firstStartRotation = finger.firstBone.localRotation;

        if (finger.secondBone != null)
            finger.secondStartRotation = finger.secondBone.localRotation;

        if (finger.thirdBone != null)
            finger.thirdStartRotation = finger.thirdBone.localRotation;
    }

    private void ApplyFingerRotation(FingerBones finger)
    {
        if (finger.firstBone != null)
        {
            float angle = finger.invertFirst ? finger.firstAngle : -finger.firstAngle;
            finger.firstBone.localRotation = finger.firstStartRotation * GetAxisRotation(finger.bendAxis, angle);
        }

        if (finger.secondBone != null)
        {
            float angle = finger.invertSecond ? finger.secondAngle : -finger.secondAngle;
            finger.secondBone.localRotation = finger.secondStartRotation * GetAxisRotation(finger.bendAxis, angle);
        }

        if (finger.thirdBone != null)
        {
            float angle = finger.invertThird ? finger.thirdAngle : -finger.thirdAngle;
            finger.thirdBone.localRotation = finger.thirdStartRotation * GetAxisRotation(finger.bendAxis, angle);
        }
    }

    private Quaternion GetAxisRotation(FingerRotationAxis axis, float angle)
    {
        switch (axis)
        {
            case FingerRotationAxis.X:
                return Quaternion.Euler(angle, 0f, 0f);
            case FingerRotationAxis.Y:
                return Quaternion.Euler(0f, angle, 0f);
            case FingerRotationAxis.Z:
                return Quaternion.Euler(0f, 0f, angle);
            default:
                return Quaternion.identity;
        }
    }

    public void SetFinger(
        FingerBones finger,
        float firstAngle,
        float secondAngle,
        float thirdAngle)
    {
        finger.firstAngle = firstAngle;
        finger.secondAngle = secondAngle;
        finger.thirdAngle = thirdAngle;
    }

    public void SetThumb(float firstAngle, float secondAngle)
    {
        thumb.firstAngle = firstAngle;
        thumb.secondAngle = secondAngle;
        thumb.thirdAngle = 0f;
    }

    public void SetIndex(float firstAngle, float secondAngle, float thirdAngle)
    {
        SetFinger(index, firstAngle, secondAngle, thirdAngle);
    }

    public void SetMiddle(float firstAngle, float secondAngle, float thirdAngle)
    {
        SetFinger(middle, firstAngle, secondAngle, thirdAngle);
    }

    public void SetRing(float firstAngle, float secondAngle, float thirdAngle)
    {
        SetFinger(ring, firstAngle, secondAngle, thirdAngle);
    }

    public void SetPinky(float firstAngle, float secondAngle, float thirdAngle)
    {
        SetFinger(pinky, firstAngle, secondAngle, thirdAngle);
    }
}