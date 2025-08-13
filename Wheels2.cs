using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Wheels2 : MonoBehaviour
{
    public WheelCollider[] Left;
    public WheelCollider[] Right;

    public float Left_motor_Tq = 0;
    public float  Right_motor_Tq = 0;

    public Rigidbody rb0;
    public Rigidbody rb1;
    public Rigidbody rb2;
    public Rigidbody rb3;
    public Rigidbody rb4;
    public Rigidbody rb5;

    public float torqueStrength = 200f;
    public float buttom_motor_Tq = 200f;
    public float buttom_motor_Tq_bl = 200f;

    public Vector3 rb0RotationAxis = Vector3.right;
    public Vector3 rb0RotationAxis2 = Vector3.left;
    public Vector3 rb1RotationAxis = Vector3.up;
    public Vector3 rb1RotationAxis2 = Vector3.down;
 

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        for (int fFor = 0; fFor < Left.Length; fFor++)
        {
            Left[fFor].motorTorque = Left_motor_Tq;
        }

        for (int fFor = 0; fFor < Right.Length; fFor++)
        {
            Right[fFor].motorTorque = Right_motor_Tq;
        }

        if (Input.GetKey(KeyCode.W))
        {
            Left_motor_Tq = 1500;
            Right_motor_Tq = 1500;
        }

        if (Input.GetKey(KeyCode.S))
        {
            Left_motor_Tq = -1500;
            Right_motor_Tq = -1500;
        }

        if (Input.GetKey(KeyCode.A))
        {
            Left_motor_Tq = -1500;
            Right_motor_Tq = 1500;
        }

        if (Input.GetKey(KeyCode.D))
        {
            Left_motor_Tq = 1500;
            Right_motor_Tq = -1500;
        }

        if (Input.GetKey(KeyCode.Q))
        {
            Left_motor_Tq = 0;
            Right_motor_Tq = 0;
        }

        if (Input.GetKey(KeyCode.Z))
        {
            rb0.AddRelativeTorque(rb0RotationAxis * buttom_motor_Tq);
        }

        if (Input.GetKey(KeyCode.X))
        {

            rb0.AddRelativeTorque(rb0RotationAxis2 * buttom_motor_Tq);
        }

        if (Input.GetKey(KeyCode.C))
        {
            rb1.AddRelativeTorque(rb1RotationAxis * torqueStrength);
        }

        if (Input.GetKey(KeyCode.V))
        {
            rb1.AddRelativeTorque(rb1RotationAxis2 * torqueStrength);
        }


        rb0.AddRelativeTorque(rb0RotationAxis * buttom_motor_Tq_bl); 
        rb0.AddRelativeTorque(rb0RotationAxis2 * buttom_motor_Tq_bl);        
       
        
    }
}
